import shutil
from html.parser import HTMLParser
from pathlib import Path

from slugify import slugify as _slugify


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_data(self):
        return "".join(self.text)


def slugify(text: str) -> str:
    return _slugify(text, lowercase=False)


def clear_path(path: Path) -> None:
    if not path.exists() or not path.is_dir():
        return

    for f in path.iterdir():
        if f.is_file():
            f.unlink()
        elif f.is_dir():
            shutil.rmtree(f)
