import re
from typing import Sequence

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.rules_inline import StateInline
from markdown_it.token import Token
from markdown_it.utils import EnvType, OptionsDict

MARK_PATTERN = re.compile(r"==+(.*?)==+")


def mark_plugin(md: MarkdownIt) -> None:
    """markdown-it-py 插件: 支持 mark 语法的解析与渲染"""
    md.inline.ruler.before("text", "mark", _mark_rule)
    md.add_render_rule("mark", _render_mark)


def _mark_rule(state: StateInline, silent: bool) -> bool:
    match = MARK_PATTERN.match(state.src[state.pos :])
    if not match:
        return False

    if not silent:
        token = state.push("mark", "mark", 0)
        token.content = match.group(1)
        state.pos += match.end()

    return True


def _render_mark(
    renderer: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    token = tokens[idx]
    return f"<mark>{token.content}</mark>"
