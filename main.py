import argparse
import asyncio
import logging
import shutil
import tomllib
from datetime import datetime
from functools import cached_property
from html.parser import HTMLParser
from math import ceil
from pathlib import Path
from typing import Literal, Sequence

import frontmatter
from mako.lookup import TemplateLookup
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.texmath import texmath_plugin
from pagefind.index import IndexConfig, PagefindIndex
from pydantic import BaseModel, TypeAdapter

# from slugify import slugify
from sqlmodel import (
    Field,
    Relationship,
    Session,
    SQLModel,
    create_engine,
    desc,
    func,
    select,
)

from mdit_plugins import (
    image_handler_plugin,
    mark_plugin,
    table_container_plugin,
)
from mdit_plugins.image_handler import ImageHandlerEnv

parser = argparse.ArgumentParser()
parser.add_argument("--src", type=str, required=True, help="源文件路径")
parser.add_argument("--dst", type=str, default="dist", help="输出文件路径")
args = parser.parse_args()


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_data(self):
        return "".join(self.text)


class Link(BaseModel):
    href: str
    name: str


class SiteTitleConfig(BaseModel):
    main: str = ""
    sub: str | None = None


class SiteIndexConfig(BaseModel):
    max_posts: int = 5


class SiteConfig(BaseModel):
    website_address: str
    customized_footer: str
    title: SiteTitleConfig
    index: SiteIndexConfig


class FriendInfo(BaseModel):
    name: str
    link: str
    desc: str


type FriendsConfig = dict[str, list[FriendInfo]]


class PostMeta(BaseModel):
    title: str | None = None
    post_date: datetime
    tags: list[str] = []


class PostTagLink(SQLModel, table=True):
    post_id: int | None = Field(default=None, foreign_key="post.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    title: str
    date: datetime
    content: str

    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="posts")

    tags: list[Tag] = Relationship(back_populates="posts", link_model=PostTagLink)

    @cached_property
    def link(self) -> str:
        return (
            (Path("/posts") / self.category.name / self.filename)
            .with_suffix(".html")
            .as_posix()
        )

    @cached_property
    def intro(self) -> str:
        s = MLStripper()
        s.feed(self.content)
        content = s.get_data()
        return s.get_data()[:60] + "..." if len(content) > 60 else content


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    posts: list[Post] = Relationship(back_populates="category")

    @cached_property
    def link(self) -> str:
        return f"/posts/{self.name}/_/post_list_1.html"


class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    posts: list[Post] = Relationship(back_populates="tags", link_model=PostTagLink)

    @cached_property
    def link(self) -> str:
        return f"/tags/{self.name}/"


class PageMeta(BaseModel):
    title: str | None = None


class Page(BaseModel):
    title: str
    filename: str
    content: str

    @cached_property
    def link(self) -> str:
        return (Path("/") / self.filename).with_suffix(".html").as_posix()


async def build_index(directory: str | Path, output: str | Path, website_address: str):
    """扫描目录，排除指定文件，生成索引"""

    html_files = Path(directory).glob("**/posts/*/*.html")
    html_files = [f for f in html_files if f.name != "index.html"]

    if not html_files:
        return

    config = IndexConfig(output_path=str(output), verbose=False)

    async with PagefindIndex(config=config) as index:
        for filepath in html_files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            url = website_address + "/" + filepath.relative_to(directory).as_posix()

            await index.add_html_file(
                content=content, url=url, source_path=str(filepath)
            )


db = create_engine("sqlite:///:memory:")

SQLModel.metadata.create_all(db)

logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

input_path = Path(args.src)
configs_path = input_path / "configs"
pages_path = input_path / "pages"
posts_path = input_path / "posts"

output_path = Path(args.dst)
output_path.mkdir(exist_ok=True)
for f in output_path.iterdir():
    if f.is_file():
        f.unlink()
    elif f.is_dir():
        shutil.rmtree(f)

attachment_path = output_path / "attachments"

assets_path = Path("assets")
tempaltes = TemplateLookup(
    directories=[assets_path / "templates"],
    input_encoding="utf-8",
)

base_template = tempaltes.get_template("base.mako")
post_template = tempaltes.get_template("post_main.mako")
post_list_template = tempaltes.get_template("post_list.mako")
page_template = tempaltes.get_template("page.mako")

markdown_compiler = (
    MarkdownIt(
        "commonmark",
        {
            "breaks": False,
            "html": True,
            "tasklists": True,
            "alerts": True,
        },
    )
    .enable("table")
    .enable("strikethrough")
    # .use(front_matter_plugin)
    .use(footnote_plugin)
    .use(texmath_plugin)
    .use(mark_plugin)
    .use(table_container_plugin)
    .use(image_handler_plugin)
)

logger.info("正在加载站点配置")
site_config = SiteConfig.model_validate(
    tomllib.load(open(configs_path / "site.toml", "rb"))
)

navbar_links = [Link(href=site_config.website_address, name="我的文章")]

friends: FriendsConfig | None = None
if (configs_path / "friends.toml").exists():
    logger.info("检测到友情链接配置, 将生成友情链接页面")
    friends = TypeAdapter(FriendsConfig).validate_python(
        tomllib.load(open(configs_path / "friends.toml", "rb"))
    )
    navbar_links.append(
        Link(href=site_config.website_address + "/friends.html", name="友情链接")
    )


logger.info("正在扫描与编译自定义页面")

pages: list[Page] = []
for page_file in (input_path / "pages").iterdir():
    if page_file.is_file() and page_file.suffix == ".md":
        md_env: ImageHandlerEnv = {
            "website_address": site_config.website_address,
            "post_path": page_file,
            "attachment_path": attachment_path,
        }
        page_meta, page_content = frontmatter.parse(page_file.read_text())
        page_meta = PageMeta.model_validate(page_meta)
        page_content = markdown_compiler.render(page_content, env=dict(md_env))
        page = Page(
            filename=page_file.name,
            title=page_meta.title or page_file.name.removesuffix(".md"),
            content=page_content,
        )
        pages.append(page)
        navbar_links.append(
            Link(
                href=site_config.website_address + page.link,
                name=page.title,
            )
        )


logger.info("正在创建导航栏与底部栏")

navbar = tempaltes.get_template("navbar.mako").render(
    title=site_config.title.main,
    links=navbar_links,
)

footer = tempaltes.get_template("footer.mako").render(
    website_address=site_config.website_address,
    customized_footer=site_config.customized_footer,
)


def gen_page(
    filepath: str | Path,
    title=site_config.title.main,
    sub_title=site_config.title.sub,
    navbar=navbar,
    main: str | bytes = "enter your main content here",
    footer=footer,
    codeblock_enable=False,
    latex_enable=False,
    image_enable=False,
) -> None:
    content = base_template.render(
        title=title,
        sub_title=sub_title,
        navbar=navbar,
        main=main,
        footer=footer,
        codeblock_enable=codeblock_enable,
        latex_enable=latex_enable,
        image_enable=image_enable,
        website_address=site_config.website_address,
    ).lstrip()

    mode: Literal["w", "wb"]
    if isinstance(content, str):
        mode = "w"
    elif isinstance(content, bytes):
        mode = "wb"
    else:
        raise TypeError("content is not str or bytes")

    with open(filepath, mode) as f:
        f.write(content)


logger.info("正在导入主题文件")

shutil.copytree(
    src=assets_path / "css",
    dst=output_path / "css",
    dirs_exist_ok=True,
)
shutil.copytree(
    src=assets_path / "fonts",
    dst=output_path / "fonts",
    dirs_exist_ok=True,
)
shutil.copytree(
    src=assets_path / "js",
    dst=output_path / "js",
    dirs_exist_ok=True,
)
shutil.copytree(
    src=assets_path / "attachments",
    dst=output_path / "attachments",
)
shutil.copyfile(
    src=assets_path / "favicon.ico",
    dst=output_path / "favicon.ico",
)

logger.info("正在扫描与编译文章")

(output_path / "posts").mkdir(exist_ok=True)

(output_path / "tags").mkdir(exist_ok=True)

for category_dir in (input_path / "posts").iterdir():
    if category_dir.is_dir():
        category = Category(name=category_dir.name)
        with Session(db) as session:
            session.add(category)
            session.commit()
            session.refresh(category)

    for post_file in category_dir.iterdir():
        if post_file.is_file() and post_file.suffix == ".md":
            md_env = {
                "website_address": site_config.website_address,
                "post_path": post_file,
                "attachment_path": attachment_path,
            }
            post_meta, post_content = frontmatter.parse(post_file.read_text())
            post_meta = PostMeta.model_validate(post_meta)

            tags: Sequence[Tag] = []
            with Session(db) as session:
                for tag_name in post_meta.tags:
                    tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
                    if not tag:
                        tag = session.merge(Tag(name=tag_name))
                    tags.append(tag)
                session.commit()
                for tag in tags:
                    session.refresh(tag)

            post_content = markdown_compiler.render(post_content, env=dict(md_env))
            post = Post(
                filename=post_file.name,
                title=post_meta.title or post_file.name.removesuffix(".md"),
                date=post_meta.post_date,
                content=post_content,
                category_id=category.id,  # type: ignore
            )
            with Session(db) as session:
                session.add(post)
                session.commit()
                session.refresh(post)

            # 完成 Tag 和 Post 的链接
            with Session(db) as session:
                for tag in tags:
                    session.add(PostTagLink(post_id=post.id, tag_id=tag.id))
                session.commit()

logger.info("正在生成侧边栏")

with Session(db) as session:
    sidebar = (
        tempaltes.get_template("sidebar.mako")
        .render(
            website_address=site_config.website_address,
            posts=session.exec(select(Post).order_by(desc(Post.date))).fetchmany(3),
            categories=session.exec(
                select(Category)
                .where(select(Post).where(Post.category_id == Category.id).exists())
                .order_by(Category.name)
            ).all(),
            tags=session.exec(select(Tag).order_by(Tag.name)).all(),
        )
        .lstrip()
    )

logger.info("正在生成文章分类展示页")

with Session(db) as session:
    categories = session.exec(
        select(Category).where(
            select(Post).where(Post.category_id == Category.id).exists()
        )
    ).all()
    for category in categories:
        (output_path / "posts" / category.name).mkdir(exist_ok=True)
        (output_path / "posts" / category.name / "_").mkdir(exist_ok=True)

        posts = category.posts
        total_post = len(posts)

        page_size = site_config.index.max_posts
        total_page = ceil(total_post / page_size)

        for page in range(1, total_page + 1):
            offset = (page - 1) * page_size

            gen_page(
                filepath=output_path
                / "posts"
                / category.name
                / "_"
                / f"post_list_{page}.html",
                sub_title=category.name,
                main=post_list_template.render(
                    title=f"Category: {category.name}",
                    posts=posts[offset : offset + page_size],
                    total_page=total_page,
                    current_page=page,
                    website_address=site_config.website_address,
                    sidebar=sidebar,
                ),
            )

        (output_path / "posts" / category.name / "index.html").write_text(
            '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Redirecting...</title></head><body><script>window.location.replace("_/post_list_1.html");</script></body></html>'
        )


logger.info("正在生成文章标签展示页")

with Session(db) as session:
    tags = session.exec(select(Tag)).all()
    for tag in tags:
        (output_path / "tags" / tag.name).mkdir(exist_ok=True)

        posts = tag.posts
        total_post = len(posts)
        page_size = site_config.index.max_posts
        total_page = ceil(total_post / page_size)

        for page in range(1, total_page + 1):
            offset = (page - 1) * page_size

            gen_page(
                filepath=output_path / "tags" / tag.name / f"post_list_{page}.html",
                sub_title=tag.name,
                main=post_list_template.render(
                    title=f"Tag: {tag.name}",
                    posts=posts[offset : offset + page_size],
                    total_page=total_page,
                    current_page=page,
                    website_address=site_config.website_address,
                    sidebar=sidebar,
                ),
            )

        shutil.copyfile(
            output_path / "tags" / tag.name / "post_list_1.html",
            output_path / "tags" / tag.name / "index.html",
        )


logger.info("正在生成所有文章")
with Session(db) as session:
    posts = session.exec(select(Post)).all()
    for post in posts:
        gen_page(
            filepath=(
                output_path / "posts" / post.category.name / post.filename
            ).with_suffix(".html"),
            title=post.title,
            sub_title=None,
            main=post_template.render(
                post=post, website_address=site_config.website_address
            ),
            codeblock_enable=True,
            latex_enable=True,
            image_enable=True,
        )


logger.info("正在编译静态索引")

asyncio.run(
    build_index(output_path, output_path / "pagefind", site_config.website_address)
)

search_page = tempaltes.get_template("search.mako").render(
    navbar=navbar,
    sidebar=sidebar,
    footer=footer,
    website_address=site_config.website_address,
)
if isinstance(search_page, str):
    (output_path / "search.html").write_text(search_page)
elif isinstance(search_page, bytes):
    (output_path / "search.html").write_bytes(search_page)

logger.info("正在生成文章列表")

# FIXME: 要思考一下如果一篇文章都没有该怎么办
with Session(db) as session:
    total_post = session.exec(select(func.count()).select_from(Post)).one()

page_size = site_config.index.max_posts
total_page = ceil(total_post / page_size)

for page in range(1, total_page + 1):
    offset = (page - 1) * page_size
    query_post = select(Post).order_by(desc(Post.date)).offset(offset).limit(page_size)

    with Session(db) as session:
        posts = session.exec(query_post).all()

        gen_page(
            filepath=output_path / f"post_list_{page}.html",
            main=post_list_template.render(
                title="我的文章",
                posts=posts,
                total_page=total_page,
                current_page=page,
                website_address=site_config.website_address,
                sidebar=sidebar,
            ),
        )

logger.info("正在生成主页")

shutil.copyfile(output_path / "post_list_1.html", output_path / "index.html")

if friends:
    logger.info("正在生成友情链接页面")
    gen_page(
        filepath=output_path / "friends.html",
        sub_title="友情链接",
        main=tempaltes.get_template("friends.mako").render(config=friends),
    )

logger.info("正在生成自定义页面")

for page in pages:
    gen_page(
        filepath=(output_path / page.filename).with_suffix(".html"),
        sub_title=page.title,
        main=page_template.render(
            main=page.content,
            sidebar=sidebar,
        ),
        codeblock_enable=True,
    )

logger.info("正在生成网站地图")

with Session(db) as session:
    posts = session.exec(select(Post)).all()
    sitemap_page = tempaltes.get_template("sitemap.mako").render(
        website_address=site_config.website_address, posts=posts, pages=pages
    )
if isinstance(sitemap_page, str):
    (output_path / "sitemap.xml").write_text(sitemap_page)
elif isinstance(sitemap_page, bytes):
    (output_path / "sitemap.xml").write_bytes(sitemap_page)

logger.info("正在导入云函数")

shutil.copytree(
    src=assets_path / "edgeone/cloud-functions",
    dst=output_path / "cloud-functions",
    dirs_exist_ok=True,
)
