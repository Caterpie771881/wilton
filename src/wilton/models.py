from datetime import datetime
from functools import cached_property
from pathlib import Path

from sqlmodel import Field, Relationship, SQLModel

from wilton.utils import MLStripper, slugify


class PostTagLink(SQLModel, table=True):
    """Post - Tag 多对多关联辅助表"""

    post_id: int | None = Field(default=None, foreign_key="post.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)


class Post(SQLModel, table=True):
    """'文章' 数据模型"""

    id: int | None = Field(default=None, primary_key=True)
    filename: str
    title: str
    date: datetime
    content: str

    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="posts")

    tags: list[Tag] = Relationship(back_populates="posts", link_model=PostTagLink)

    @cached_property
    def slug_filename(self) -> str:
        return slugify(self.filename)

    @cached_property
    def link(self) -> str:
        return (
            (Path("/posts") / self.category.slug_name / self.slug_filename)
            .with_suffix(".html")
            .as_posix()
        )

    @cached_property
    def intro(self) -> str:
        if self.content is None:
            return ""

        s = MLStripper()
        s.feed(self.content)
        content = s.get_data()
        return s.get_data()[:60] + "..." if len(content) > 60 else content


class Category(SQLModel, table=True):
    """'分类' 数据模型"""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    posts: list[Post] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"order_by": "desc(Post.date)"},
    )

    @cached_property
    def slug_name(self) -> str:
        return slugify(self.name)

    @cached_property
    def link(self) -> str:
        return f"/posts/{self.slug_name}/_/post_list_1.html"


class Tag(SQLModel, table=True):
    """'标签' 数据模型"""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    posts: list[Post] = Relationship(
        back_populates="tags",
        link_model=PostTagLink,
        sa_relationship_kwargs={"order_by": "desc(Post.date)"},
    )

    @cached_property
    def slug_name(self) -> str:
        return slugify(self.name)

    @cached_property
    def link(self) -> str:
        return f"/tags/{self.slug_name}/"


class Page(SQLModel, table=True):
    """'页面' 数据模型"""

    id: int | None = Field(default=None, primary_key=True)
    title: str
    filename: str
    content: str

    @cached_property
    def slug_filename(self) -> str:
        return slugify(self.filename)

    @cached_property
    def link(self) -> str:
        return (Path("/") / self.slug_filename).with_suffix(".html").as_posix()
