from datetime import datetime
from pathlib import Path
from typing import Sequence

import frontmatter
from pydantic import BaseModel, ValidationError
from sqlalchemy import Engine
from sqlmodel import Session, select

from wilton.core.logging import logger
from wilton.models import Category, Page, Post, PostTagLink, Tag


class PostMeta(BaseModel):
    """文章元数据"""

    title: str | None = None
    post_date: datetime
    tags: list[str] = []
    draft: bool = False


class PageMeta(BaseModel):
    """页面元数据"""

    title: str | None = None
    draft: bool = False


class Scanner:
    """扫描器, 负责扫描用户提供的博客目录, 找到所有的文章、分类、标签、页面"""

    def __init__(self, source_path: Path, db: Engine) -> None:
        self.source_path = source_path
        self.post_path = source_path / "posts"
        self.page_path = source_path / "pages"
        self.db = db

    def scan_posts(self) -> None:
        """
        扫描文章目录, 构建 文章-分类-标签 数据表
        该步骤会解析文章的元数据, 但不会进行编译
        """
        logger.info("开始扫描文章目录")

        if not self.post_path.exists():
            logger.error("无法扫描文章目录: 目录不存在")
            return

        if not self.post_path.is_dir():
            logger.error("无法扫描文章目录: 这不是一个目录")
            return

        for category_dir in self.post_path.iterdir():
            self.scan_category_dir(category_dir)

    def scan_category_dir(self, category_dir: Path) -> None:
        """扫描分类目录"""
        if not category_dir.is_dir():
            return

        logger.info(f"发现分类目录: {category_dir}")
        category = Category(name=category_dir.name)
        with Session(self.db) as session:
            session.add(category)
            session.commit()
            session.refresh(category)

        for post_file in category_dir.iterdir():
            self.handle_post_file(post_file, category)

    def handle_post_file(self, post_file: Path, category: Category) -> None:
        """解析文章"""
        if not post_file.is_file() or post_file.suffix != ".md":
            return

        logger.info(f"发现文章: {post_file}")

        try:
            post_meta, post_content = frontmatter.parse(post_file.read_text())
            post_meta = PostMeta.model_validate(post_meta)
        except ValidationError as e:
            logger.error(f"解析元数据失败, 失败原因: {e}")
            return

        if post_meta.draft:
            logger.info(f"文章为草稿状态, 将跳过: {post_file}")
            return

        filename = post_file.name.removesuffix(".md")
        post = Post(
            filename=filename,
            title=post_meta.title or filename,
            date=post_meta.post_date,
            content=post_content,
            category_id=category.id,  # type: ignore
        )
        with Session(self.db) as session:
            session.add(post)
            session.commit()
            session.refresh(post)

        self.record_tags(post, post_meta.tags)

    def record_tags(self, post: Post, tag_names: list[str]) -> None:
        """记录标签"""
        tags: Sequence[Tag] = []

        with Session(self.db) as session:
            for tag_name in tag_names:
                tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
                if not tag:
                    logger.info(f"发现标签: {tag_name}")
                    tag = session.merge(Tag(name=tag_name))
                tags.append(tag)

            session.commit()
            for tag in tags:
                session.refresh(tag)

        # 完成 Tag 和 Post 的链接
        with Session(self.db) as session:
            for tag in tags:
                session.add(PostTagLink(post_id=post.id, tag_id=tag.id))
            session.commit()

    def scan_pages(self) -> None:
        """
        扫描页面目录, 构建页面数据表
        该步骤会解析页面的元数据, 但不会进行编译
        """
        logger.info("开始扫描页面目录")

        if not self.page_path.exists():
            logger.error("无法扫描页面目录: 目录不存在")
            return

        if not self.page_path.is_dir():
            logger.error("无法扫描页面目录: 这不是一个目录")
            return

        for page_file in self.page_path.iterdir():
            self.handle_page_file(page_file)

    def handle_page_file(self, page_file: Path) -> None:
        """解析页面"""
        if not page_file.is_file() or page_file.suffix != ".md":
            return

        logger.info(f"发现页面: {page_file}")

        try:
            page_meta, page_content = frontmatter.parse(page_file.read_text())
            page_meta = PageMeta.model_validate(page_meta)
        except ValidationError as e:
            logger.error(f"解析元数据失败, 失败原因: {e}")
            return

        if page_meta.draft:
            logger.info(f"页面为草稿状态, 将跳过: {page_file}")
            return

        filename = page_file.name.removesuffix(".md")
        page = Page(
            filename=filename,
            title=page_meta.title or filename,
            content=page_content,
        )

        with Session(self.db) as session:
            session.add(page)
            session.commit()
