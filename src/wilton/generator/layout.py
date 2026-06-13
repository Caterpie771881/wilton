from pydantic import BaseModel
from sqlalchemy import Engine
from sqlmodel import Session, desc, select

from wilton.config import FriendsConfig, SiteConfig
from wilton.core.logging import logger
from wilton.core.template import TemplateLookup
from wilton.models import Category, Page, Post, Tag

__all__ = ["LayoutGenerator"]


class Link(BaseModel):
    """辅助结构体, 用于表示一个链接"""

    href: str
    name: str


class LayoutGenerator:
    def __init__(
        self,
        site_config: SiteConfig,
        friends_config: FriendsConfig | None,
        db: Engine,
        templates: TemplateLookup,
    ) -> None:
        self.site_config = site_config
        self.friends_config = friends_config
        self.db = db
        self.templates = templates

    def gen_navbar(self) -> str:
        """生成导航栏"""
        logger.info("正在生成导航栏")

        links: list[Link] = []

        links.append(Link(href=self.site_config.website_address, name="我的文章"))
        if self.friends_config:
            href = self.site_config.website_address + "/friends.html"
            links.append(Link(href=href, name="友情链接"))

        with Session(self.db) as session:
            pages = session.exec(select(Page)).all()

        for page in pages:
            links.append(Link(href=page.link, name=page.title))

        return self.templates.get_component_tmpl("navbar.mako").render(
            title=self.site_config.title.main,
            links=links,
        )

    def gen_footer(self) -> str:
        """生成底部栏"""
        logger.info("正在生成底部栏")

        return self.templates.get_component_tmpl("footer.mako").render(
            website_address=self.site_config.website_address,
            customized_footer=self.site_config.customized_footer,
        )

    def gen_sidebar(self, components: list[str] = []) -> str:
        """生成侧边栏"""
        logger.info(f"正在生成侧边栏, 包含组件: {','.join(components)}")

        _components = []
        for name in components:
            component = self.gen_sidebar_component(name)
            if component:
                _components.append(component)

        return self.templates.get_component_tmpl("sidebar.mako").render(
            components=_components
        )

    def gen_sidebar_component(self, name: str) -> str | None:
        match name:
            case "catalogue":
                return self.templates.get_component_tmpl(
                    "sidebar/catalogue.mako"
                ).render()
            case "cateory_list":
                return self.gen_cateory_list()
            case "recent_posts":
                return self.gen_recent_posts()
            case "search_box":
                return self.templates.get_component_tmpl(
                    "sidebar/search_box.mako"
                ).render()
            case "tag_cloud":
                return self.gen_tag_cloud()
            case _:
                logger.warning(f"不存在的组件: {name}")

    def gen_cateory_list(self) -> str:
        """生成侧边栏模块: 文章类别"""
        query = (
            select(Category)
            .where(select(Post).where(Post.category_id == Category.id).exists())
            .order_by(Category.name)
        )
        with Session(self.db) as session:
            categories = session.exec(query).all()
            return self.templates.get_component_tmpl(
                "sidebar/cateory_list.mako"
            ).render(
                website_address=self.site_config.website_address,
                categories=categories,
            )

    def gen_recent_posts(self) -> str:
        """生成侧边栏模块: 最近文章"""
        query = select(Post).order_by(desc(Post.date))
        with Session(self.db) as session:
            posts = session.exec(query).fetchmany(3)
            return self.templates.get_component_tmpl(
                "sidebar/recent_posts.mako"
            ).render(
                website_address=self.site_config.website_address,
                posts=posts,
            )

    def gen_tag_cloud(self) -> str:
        """生成侧边栏模块: 标签云"""
        query = select(Tag).order_by(Tag.name)
        with Session(self.db) as session:
            tags = session.exec(query).all()
            return self.templates.get_component_tmpl("sidebar/tag_cloud.mako").render(
                website_address=self.site_config.website_address,
                tags=tags,
            )
