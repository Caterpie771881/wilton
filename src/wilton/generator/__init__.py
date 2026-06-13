from math import ceil
from pathlib import Path
from typing import Sequence

from pydantic import BaseModel
from sqlalchemy import Engine
from sqlmodel import Session, select

from wilton.config import FriendsConfig, SiteConfig
from wilton.core.logging import logger
from wilton.core.template import TemplateLookup
from wilton.generator.layout import LayoutGenerator
from wilton.models import Category, Page, Post, Tag

__all__ = ["Generator"]


class TmplContext(BaseModel):
    """模版上下文"""

    config: SiteConfig
    navbar: str
    footer: str


class Generator:
    """生成器, 根据扫描器的产物, 编译并生成实际的 html 页面"""

    def __init__(
        self,
        site_config: SiteConfig,
        friends_config: FriendsConfig | None,
        source_path: Path,
        dist_path: Path,
        db: Engine,
        templates: TemplateLookup,
    ) -> None:
        self.site_config = site_config
        self.friends_config = friends_config
        self.source_path = source_path
        self.dist_path = dist_path
        self.db = db
        self.templates = templates

        self.layout = LayoutGenerator(
            site_config=site_config,
            friends_config=friends_config,
            db=db,
            templates=templates,
        )

        self.sidebar_default = self.layout.gen_sidebar(
            ["search_box", "recent_posts", "cateory_list", "tag_cloud"]
        )
        self.sidebar_for_post = self.layout.gen_sidebar(["search_box", "catalogue"])

        self.tmpl_ctx = TmplContext(
            config=self.site_config,
            navbar=self.layout.gen_navbar(),
            footer=self.layout.gen_footer(),
        )

    def gen_dist(self) -> None:
        self.gen_posts_dir()
        self.gen_tags_dir()
        self.gen_post_list_for_posts()
        self.gen_pages()
        self.gen_site_map()

    def gen_posts_dir(self) -> None:
        query = (
            select(Category)
            .where(select(Post).where(Post.category_id == Category.id).exists())
            .order_by(Category.name)
        )
        with Session(self.db) as session:
            categories = session.exec(query).all()

            for category in categories:
                category_dir = self.dist_path / "posts" / category.slug_name
                category_dir.mkdir(parents=True, exist_ok=True)
                self.gen_post_list_for_category(category, category_dir / "_")

                for post in category.posts:
                    post_path = category_dir / post.slug_filename
                    content = self.templates.get_tmpl("post.mako").render(
                        ctx=self.tmpl_ctx,
                        post=post,
                        sidebar=self.sidebar_for_post,
                        codeblock_enable=True,
                        latex_enable=True,
                        image_enable=True,
                    )
                    post_path.with_suffix(".html").write_text(content)

    def gen_post_list(
        self,
        posts: Sequence[Post],
        target_path: Path,
        options: dict = {},
    ) -> None:
        total_post = len(posts)
        page_size = self.site_config.index.max_posts
        total_page = ceil(total_post / page_size)

        for page in range(1, total_page + 1):
            offset = (page - 1) * page_size
            content = self.templates.get_tmpl("post_list.mako").render(
                ctx=self.tmpl_ctx,
                posts=posts[offset : offset + page_size],
                sidebar=self.sidebar_default,
                total_page=total_page,
                current_page=page,
                **options,
            )
            (target_path / f"post_list_{page}.html").write_text(content)

    def gen_post_list_for_category(self, category: Category, target_path: Path) -> None:
        """生成指定类别的文章列表"""
        target_path.mkdir(exist_ok=True)
        self.gen_post_list(
            category.posts,
            target_path,
            {"sub_title": category.name, "title": f"Category: {category.name}"},
        )

        (target_path / "../index.html").write_text(
            self.templates.get_tmpl("redirect.mako").render(target="_/post_list_1.html")
        )

    def gen_tags_dir(self) -> None:
        """生成所有标签的文章列表"""
        with Session(self.db) as session:
            tags = session.exec(select(Tag)).all()
            for tag in tags:
                tag_dir = self.dist_path / "tags" / tag.slug_name
                tag_dir.mkdir(parents=True, exist_ok=True)
                self.gen_post_list_for_tag(tag, tag_dir)

    def gen_post_list_for_tag(self, tag: Tag, target_path: Path) -> None:
        """生成指定标签的文章列表"""
        self.gen_post_list(
            tag.posts,
            target_path,
            {"sub_title": tag.name, "title": f"Tag: {tag.name}"},
        )
        (target_path / "post_list_1.html").copy(target_path / "index.html")

    def gen_post_list_for_posts(self) -> None:
        with Session(self.db) as session:
            posts = session.exec(select(Post)).all()

            total_post = len(posts)
            if total_post == 0:
                content = self.templates.get_tmpl("zero_post.mako").render(
                    ctx=self.tmpl_ctx,
                    sidebar=self.sidebar_default,
                )
                (self.dist_path / "index.html").write_text(content)
                return

            self.gen_post_list(posts, self.dist_path, {"title": "我的文章"})

        (self.dist_path / "post_list_1.html").copy(self.dist_path / "index.html")

    def gen_pages(self) -> None:
        """生成所有页面"""
        logger.info("正在生成页面")

        if self.friends_config:
            self.gen_friends_page()

        self.gen_search_page()

        with Session(self.db) as session:
            pages = session.exec(select(Page)).all()

        for page in pages:
            target_path = (self.dist_path / page.slug_filename).with_suffix(".html")
            content = self.templates.get_tmpl("page.mako").render(
                ctx=self.tmpl_ctx,
                page=page,
                sidebar=self.sidebar_default,
                codeblock_enable=True,
                latex_enable=True,
                image_enable=True,
            )
            target_path.write_text(content)

    def gen_friends_page(self) -> None:
        """生成友情链接页面"""
        logger.info("正在生成友情链接页面")
        if self.friends_config is None:
            return

        content = self.templates.get_tmpl("friends.mako").render(
            ctx=self.tmpl_ctx,
            config=self.friends_config,
        )
        (self.dist_path / "friends.html").write_text(content)

    def gen_search_page(self) -> None:
        """生成搜索页"""
        logger.info("正在生成搜索页")
        content = self.templates.get_tmpl("search.mako").render(
            ctx=self.tmpl_ctx,
            sidebar=self.sidebar_default,
        )
        (self.dist_path / "search.html").write_text(content)

    def gen_site_map(self) -> None:
        """生成网站地图"""
        logger.info("正在生成网站地图")

        with Session(self.db) as session:
            posts = session.exec(select(Post)).all()
            pages = session.exec(select(Page)).all()
            content = self.templates.get_tmpl("sitemap.mako").render(
                website_address=self.site_config.website_address,
                posts=posts,
                pages=pages,
            )

        (self.dist_path / "sitemap.xml").write_text(content)
