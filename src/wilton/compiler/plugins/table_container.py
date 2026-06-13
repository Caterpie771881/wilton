from typing import Sequence

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from markdown_it.utils import EnvType, OptionsDict


def table_container_plugin(md: MarkdownIt) -> None:
    """
    markdown-it-py 插件: 将生成 table 标签用 <div class="table-container">...</div> 包裹
    """
    md.add_render_rule("table_open", _render_table_open_wrapper)
    md.add_render_rule("table_close", _render_table_close_wrapper)


def _render_table_open_wrapper(
    renderer: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    return '<div class="table-container">\n' + renderer.renderToken(
        tokens, idx, options, env
    )


def _render_table_close_wrapper(
    renderer: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    return renderer.renderToken(tokens, idx, options, env) + "</div>\n"
