from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.utils import EnvType
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.texmath import texmath_plugin
from sqlalchemy import Engine
from sqlmodel import Session, select

from wilton.config import SiteConfig
from wilton.core.logging import logger
from wilton.models import Page, Post

from .plugins.image_handler import ImageHandlerEnv, image_handler_plugin
from .plugins.mark import mark_plugin
from .plugins.table_container import table_container_plugin


class MDCompiler:
    def __init__(
        self,
        source_path: Path,
        dist_path: Path,
        site_config: SiteConfig,
        db: Engine,
    ) -> None:
        options = {
            "breaks": False,
            "html": True,
            "tasklists": True,
            "alerts": True,
        }
        self.md = (
            MarkdownIt("commonmark", options)
            .enable("table")
            .enable("strikethrough")
            .use(footnote_plugin)
            .use(texmath_plugin)
            .use(mark_plugin)
            .use(table_container_plugin)
            .use(image_handler_plugin)
        )

        self.source_path = source_path
        self.dist_path = dist_path
        self.site_config = site_config
        self.db = db

        (self.dist_path / "attachments").mkdir(exist_ok=True)

    def render(self, src: str, env: EnvType) -> str:
        return self.md.render(src, env)

    def build_env(self, post_path: Path) -> EnvType:
        """构建 markdown-it 环境变量"""
        image_handler_env: ImageHandlerEnv = {
            "website_address": self.site_config.website_address,
            "attachment_path": self.dist_path / "attachments",
            "post_path": post_path,
        }
        return dict(image_handler_env)

    def compile_posts(self) -> None:
        """编译所有文章"""
        logger.info("正在编译文章")

        with Session(self.db) as session:
            posts = session.exec(select(Post)).all()
            for post in posts:
                env = self.build_env(
                    self.source_path / "posts" / post.category.name / post.filename
                )
                post.content = self.render(post.content, env)
                session.add(post)

            session.commit()

    def compile_pages(self) -> None:
        """编译所有页面"""
        logger.info("正在编译页面")

        with Session(self.db) as session:
            pages = session.exec(select(Page)).all()
            for page in pages:
                env = self.build_env(self.source_path / "pages" / page.filename)
                page.content = self.render(page.content, env)
                session.add(page)

            session.commit()
