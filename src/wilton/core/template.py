from pathlib import Path

import minify_html
from mako.lookup import TemplateLookup as MakoTemplateLookup
from mako.template import Template as MakoTemplate

__all__ = ["TemplateLookup", "Template"]


class TemplateLookup:
    def __init__(self) -> None:
        self.templates = MakoTemplateLookup(
            directories=[Path(__file__).parent / "../templates"],
            input_encoding="utf-8",
        )

    def get_tmpl(self, uri: str, minify: bool = False) -> Template:
        return Template(self.templates.get_template(uri), minify)

    def get_component_tmpl(self, uri: str) -> Template:
        return self.get_tmpl(f"components/{uri}")


class Template:
    def __init__(self, tmpl: MakoTemplate, minify: bool = False) -> None:
        self.tmpl = tmpl
        self.minify = minify

    def render(self, *args, **data) -> str:
        result = self.tmpl.render(*args, **data)
        if isinstance(result, bytes):
            result = result.decode()
        if self.minify:
            result = minify_html.minify(
                result,
                minify_css=True,
                minify_js=True,
                keep_closing_tags=True,
                keep_html_and_head_opening_tags=True,
            )
        return result
