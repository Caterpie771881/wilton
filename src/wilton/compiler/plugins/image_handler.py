import hashlib
from pathlib import Path
from typing import Sequence, TypedDict
from urllib.parse import unquote

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from markdown_it.utils import OptionsDict

from wilton.core.logging import logger


class ImageHandlerEnv(TypedDict):
    website_address: str
    post_path: Path
    attachment_path: Path


def get_file_md5(file_path: str | Path) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def image_handler_plugin(md: MarkdownIt) -> None:
    """
    markdown-it-py 插件: 编译时将引用的图片置入特定目录, 并按照其 md5 对文件名与引用链接进行重命名
    """
    md.add_render_rule("image", _render_image)


def _render_image(
    renderer: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: ImageHandlerEnv,
) -> str:
    token = tokens[idx]

    src = token.attrGet("src")

    bronk_image_src = (
        env["website_address"] + (Path("/attachments") / "broken-image.svg").as_posix()
    )
    if not isinstance(src, str) or src.startswith(("http://", "https://")):
        token.attrSet("onerror", f"this.onerror=null;this.src='{bronk_image_src}';")
        return renderer.image(tokens, idx, options, dict(env))

    img_path = env["post_path"].parent / unquote(src)
    if not img_path.exists():
        logger.warning(f"image not exists: {img_path}")
        token.attrSet("src", bronk_image_src)
        return renderer.image(tokens, idx, options, dict(env))

    img_hash = get_file_md5(img_path)
    img_output_path = (env["attachment_path"] / img_hash).with_suffix(img_path.suffix)
    token.attrSet(
        "src",
        env["website_address"]
        + (Path("/attachments") / img_hash).with_suffix(img_path.suffix).as_posix(),
    )
    if not img_output_path.exists():
        img_path.copy(img_output_path)

    return renderer.image(tokens, idx, options, dict(env))
