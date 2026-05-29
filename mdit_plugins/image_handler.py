import hashlib
import shutil
from pathlib import Path
from typing import Any, TypedDict

from markdown_it import MarkdownIt
from markdown_it.token import Token


class ImageHandlerEnv(TypedDict):
    website_address: str
    post_path: Path
    attachment_path: Path


def get_file_md5(file_path: str | Path) -> str:
    """计算文件的 MD5 哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        # 分块读取，避免大文件内存爆炸
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _collect_image_urls(tokens: list[Token], env: ImageHandlerEnv) -> None:
    """遍历 token 列表（含 children），打印图片 token 的 src 链接。"""
    for token in tokens:
        # 识别图片 token：type 为 "image" 且标签为 "img"
        if token.type == "image" and token.tag == "img":
            src = token.attrGet("src")

            if (
                src is not None
                and isinstance(src, str)
                and not (src.startswith("http://") or src.startswith("https://"))
            ):
                img_path = env["post_path"].parent / src
                img_hash = get_file_md5(img_path)
                img_output_path = (env["attachment_path"] / img_hash).with_suffix(
                    img_path.suffix
                )
                token.attrSet(
                    "src",
                    env["website_address"]
                    + (Path("/attachment") / img_hash)
                    .with_suffix(img_path.suffix)
                    .as_posix(),
                )
                if not img_output_path.exists():
                    shutil.copyfile(src=img_path, dst=img_output_path)

        # 递归处理 children（图片 token 可能出现在 inline token 的子节点中）
        if token.children:
            _collect_image_urls(token.children, env)


def image_handler_plugin(md: MarkdownIt) -> None:
    md.core.ruler.push("print_image_urls", _print_image_urls_rule)


def _print_image_urls_rule(state: Any) -> None:
    """
    core 链的规则函数，接收 StateCore 对象，其中 state.tokens 为 token 列表。
    """
    _collect_image_urls(state.tokens, state.env)
