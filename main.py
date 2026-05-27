import logging
import shutil
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Literal, Sequence

from mako.template import Template
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.texmath import texmath_plugin
from pydantic import BaseModel, TypeAdapter
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

from front_matter import front_matter_plugin
from mark import mark_plugin

db = create_engine("sqlite:///:memory:")


class Link(BaseModel):
    href: str
    name: str


class SiteTitleConfig(BaseModel):
    main: str = ""
    sub: str | None


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
    title: str | None
    post_date: datetime
    tags: list[str]


class PostTagLink(SQLModel, table=True):
    post_id: int | None = Field(default=None, foreign_key="post.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    date: datetime
    content: str

    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="posts")

    tags: list[Tag] = Relationship(back_populates="posts", link_model=PostTagLink)

    @property
    def link(self) -> str:
        return f"/posts/{self.category.name}/{self.title}.html"


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    posts: list[Post] = Relationship(back_populates="category")

    @property
    def link(self) -> str:
        return f"/posts/{self.name}/"


class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    posts: list[Post] = Relationship(back_populates="tags", link_model=PostTagLink)

    @property
    def link(self) -> str:
        return f"/tags/{self.name}.html"


SQLModel.metadata.create_all(db)


logging.root.setLevel(logging.INFO)

input_path = Path("input")
configs_path = input_path / "configs"
pages_path = input_path / "pages"
posts_path = input_path / "posts"

output_path = Path("test-dist")

assets_path = Path("assets")
base_template = Template(filename=str(assets_path / "templates/base.mako"))
post_template = Template(filename=str(assets_path / "templates/post_main.mako"))

logging.info("正在加载站点配置")
site_config = SiteConfig.model_validate(
    tomllib.load(open(configs_path / "site.toml", "rb"))
)

navbar_links = [Link(href=site_config.website_address, name="我的文章")]

friends: FriendsConfig | None = None
if (configs_path / "friends.toml").exists():
    logging.info("检测到友情链接配置, 将生成友情链接页面")
    friends = TypeAdapter(FriendsConfig).validate_python(
        tomllib.load(open(configs_path / "friends.toml", "rb"))
    )
    navbar_links.append(
        Link(href=site_config.website_address + "/friends.html", name="友情链接")
    )

logging.info("正在创建导航栏与底部栏")

navbar = Template(filename=str(assets_path / "templates/navbar.mako")).render(
    title=site_config.title.main,
    links=navbar_links,
)

footer = Template(filename=str(assets_path / "templates/footer.mako")).render(
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
        config=site_config,
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


logging.info("正在导入主题文件")

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
shutil.copyfile(
    src=assets_path / "favicon.ico",
    dst=output_path / "favicon.ico",
)

logging.info("正在编译文章")

markdown_compiler = (
    MarkdownIt("commonmark", {"breaks": True, "html": True})
    .use(front_matter_plugin)
    .use(footnote_plugin)
    .use(texmath_plugin)
    .use(mark_plugin)
    .use(tasklists_plugin)
    .enable("table")
    .enable("strikethrough")
)

(output_path / "posts").mkdir(exist_ok=True)

(output_path / "tags").mkdir(exist_ok=True)


for category_dir in (input_path / "posts").iterdir():
    if category_dir.is_dir():
        if not (output_path / "posts" / category_dir.name).exists():
            (output_path / "posts" / category_dir.name).mkdir()

        category = Category(name=category_dir.name)
        with Session(db) as session:
            session.add(category)
            session.commit()
            session.refresh(category)

    for post_file in category_dir.iterdir():
        if post_file.is_file() and post_file.suffix == ".md":
            tokens = markdown_compiler.parse(post_file.read_text())
            if tokens and tokens[0].type == "front_matter":
                post_meta = PostMeta.model_validate(tomllib.loads(tokens[0].content))
            else:
                raise RuntimeError("post don't have metadata")

            tags: Sequence[Tag] = []
            with Session(db) as session:
                for tag_name in post_meta.tags:
                    tag = session.merge(Tag(name=tag_name))
                    tags.append(tag)
                session.commit()
                for tag in tags:
                    session.refresh(tag)

            post_content = markdown_compiler.render(post_file.read_text())
            post = Post(
                title=post_meta.title or post_file.name.removesuffix(".md"),
                date=post_meta.post_date,
                content=post_content,
                category_id=category.id,  # type: ignore
            )
            with Session(db) as session:
                session.add(post)
                session.commit()
                session.refresh(post)

            # TODO: 完成 Tag 和 Post 的链接
            with Session(db) as session:
                for tag in tags:
                    session.add(PostTagLink(post_id=post.id, tag_id=tag.id))
                session.commit()

# TODO: 生成所有 post

with Session(db) as session:
    posts = session.exec(select(Post)).all()
    for post in posts:
        gen_page(
            filepath=(
                output_path / "posts" / post.category.name / post.title
            ).with_suffix(".html"),
            title=post.title,
            sub_title=None,
            main=post_template.render(post=post, config=site_config),
            codeblock_enable=True,
            latex_enable=True,
            image_enable=True,
        )


# TODO: 生成 posts/<category>/index.html 用于展示当前类别下的所有文章
with Session(db) as session:
    categories = session.exec(select(Category)).all()
    for category in categories:
        ...

# TODO: 生成 tags/<tag>.html 用于展示当前标签下的文章
with Session(db) as session:
    tags = session.exec(select(Tag)).all()
    for tag in tags:
        ...

logging.info("正在编译静态索引")

# TODO

logging.info("正在生成文章列表")

# TODO
# ATTENTION: 要思考一下如果一篇文章都没有该怎么办

logging.info("正在生成主页")

# TODO: 其实就是把文章列表的第一页复制为 webroot/index.html

if friends:
    logging.info("正在生成友情链接页面")
    gen_page(
        filepath=output_path / "friends.html",
        sub_title="友情链接",
        main=Template(filename="assets/templates/friends.mako").render(config=friends),
    )

logging.info("正在编译自定义页面")

# TODO

logging.info("正在生成网站地图")

# TODO
