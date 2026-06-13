from pathlib import Path

from wilton.config import SiteConfig
from wilton.core.logging import logger

assets_path = Path(__file__).parent / "assets"
backend_path = Path(__file__).parent / "backend"


class AssetsLoader:
    """资源加载器, 用于加载那些依赖配置、不依赖博客内容的资源"""

    def __init__(self, dist_path: Path, site_config: SiteConfig) -> None:
        self.dist_path = dist_path
        self.site_config = site_config

    def load(self, assets: str, target: str) -> None:
        (assets_path / assets).copy(self.dist_path / target)

    def load_theme(self) -> None:
        """导入主题文件"""
        logger.info("正在导入主题")
        # TODO: 根据配置加载自定义主题
        self.load("attachments", "attachments")
        self.load("css", "css")
        self.load("js", "js")
        self.load("fonts", "fonts")

    def load_icon(self) -> None:
        """导入图标"""
        # TODO: 根据配置加载自定义图标
        self.load("favicon.ico", "favicon.ico")

    def load_backend(self) -> None:
        """导入后端组件"""
        # TODO: 根据配置选择不同后端
        logger.info("正在导入 EdgeOne 云函数")
        (backend_path / "edgeone/cloud-functions").copy(
            self.dist_path / "cloud-functions"
        )
