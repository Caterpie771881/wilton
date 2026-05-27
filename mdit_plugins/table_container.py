from typing import Any

from markdown_it import MarkdownIt
from markdown_it.token import Token


def table_container_plugin(md: MarkdownIt) -> None:
    """
    markdown-it-py 插件：将生成 table 标签用 <div class="table-container">...</div> 包裹
    """

    def render_table_open_wrapper(
        tokens: list[Token], idx: int, options: dict, env: Any
    ) -> str:
        return '<div class="table-container">\n<table>\n'

    def render_table_close_wrapper(
        tokens: list[Token], idx: int, options: dict, env: Any
    ) -> str:
        return "</table>\n</div>\n"

    # 覆盖 table_open 和 table_close 渲染规则
    md.renderer.rules["table_open"] = render_table_open_wrapper  # type: ignore
    md.renderer.rules["table_close"] = render_table_close_wrapper  # type: ignore
