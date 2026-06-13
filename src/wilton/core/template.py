from pathlib import Path

from mako.lookup import TemplateLookup as MakoTemplateLookup
from mako.template import Template as MakoTemplate

__all__ = ["TemplateLookup", "Template"]


class TemplateLookup:
    def __init__(self) -> None:
        self.templates = MakoTemplateLookup(
            directories=[Path(__file__).parent / "../templates"],
            input_encoding="utf-8",
        )

    def get_tmpl(self, uri: str) -> Template:
        return Template(self.templates.get_template(uri))

    def get_component_tmpl(self, uri: str) -> Template:
        return self.get_tmpl(f"components/{uri}")


class Template:
    def __init__(self, tmpl: MakoTemplate) -> None:
        self.tmpl = tmpl

    def render(self, *args, **data) -> str:
        result = self.tmpl.render(*args, **data)
        if isinstance(result, bytes):
            result = result.decode()
        return result
