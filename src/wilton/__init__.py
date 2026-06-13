import asyncio
from argparse import ArgumentParser, Namespace
from pathlib import Path

from pagefind.index import IndexConfig, PagefindIndex

from wilton.assets import AssetsLoader
from wilton.compiler import MDCompiler
from wilton.config import ConfigLoader
from wilton.core.database import db, init_db
from wilton.core.logging import logger
from wilton.core.template import TemplateLookup
from wilton.generator import Generator
from wilton.scanner import Scanner
from wilton.utils import clear_path


def get_args() -> Namespace:
    """解析命令行参数"""
    parser = ArgumentParser()
    parser.add_argument("--src", type=str, required=True, help="源文件路径")
    parser.add_argument("--dst", type=str, default="dist", help="输出文件路径")
    args = parser.parse_args()
    return args


async def build_index(directory: str | Path, output: str | Path, website_address: str):
    """扫描目录，排除指定文件，生成索引"""
    logger.info("正在编译静态索引")

    html_files = Path(directory).glob("**/posts/*/*.html")
    html_files = [f for f in html_files if f.name != "index.html"]

    if not html_files:
        return

    config = IndexConfig(output_path=str(output), verbose=False)

    async with PagefindIndex(config=config) as index:
        for filepath in html_files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            url = website_address + "/" + filepath.relative_to(directory).as_posix()

            await index.add_html_file(
                content=content, url=url, source_path=str(filepath)
            )


def main() -> None:
    args = get_args()
    source_path = Path(args.src)
    dist_path = Path(args.dst)

    logger.info(f"源路径: {source_path.absolute()}")
    logger.info(f"输出路径: {dist_path.absolute()}")

    dist_path.mkdir(exist_ok=True)
    clear_path(dist_path)

    init_db(db)

    # 加载配置
    config_loader = ConfigLoader(source_path)
    site_config = config_loader.load_site_config()
    if site_config is None:
        return
    friends_config = config_loader.load_friends_config()

    # 导入资源
    assets_load = AssetsLoader(
        dist_path=dist_path,
        site_config=site_config,
    )
    assets_load.load_theme()
    assets_load.load_icon()
    assets_load.load_backend()

    # 扫描博客文件夹
    scanner = Scanner(source_path, db)
    scanner.scan_posts()
    scanner.scan_pages()

    # 编译文章与页面
    compiler = MDCompiler(
        site_config=site_config,
        source_path=source_path,
        dist_path=dist_path,
        db=db,
    )
    compiler.compile_posts()
    compiler.compile_pages()

    # 生成构建产物
    generator = Generator(
        site_config=site_config,
        friends_config=friends_config,
        source_path=source_path,
        dist_path=dist_path,
        db=db,
        templates=TemplateLookup(),
    )
    generator.gen_dist()

    # TODO: 压缩 html

    # 编译静态索引
    asyncio.run(
        build_index(dist_path, dist_path / "pagefind", site_config.website_address)
    )
