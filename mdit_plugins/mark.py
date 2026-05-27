from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline


def mark_plugin(md: MarkdownIt) -> None:
    md.inline.ruler.before("text", "mark", _mark_rule)


def _mark_rule(state: StateInline, silent: bool) -> bool:
    start = state.pos

    if state.src[start : start + 2] != "==":
        return False

    end = state.src.find("==", start + 2)
    if end == -1:
        return False

    content = state.src[start + 2 : end]

    if not silent:
        token = state.push("html_inline", "", 0)
        token.content = f"<mark>{content}</mark>"

    state.pos = end + 2
    return True
