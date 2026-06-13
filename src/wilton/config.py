from pathlib import Path

import toml
from pydantic import BaseModel, TypeAdapter, ValidationError

from wilton.core.logging import logger


class SiteTitleConfig(BaseModel):
    main: str = ""
    sub: str | None = None


class SiteIndexConfig(BaseModel):
    max_posts: int = 5


class SiteConfig(BaseModel):
    website_address: str
    customized_footer: str
    title: SiteTitleConfig
    index: SiteIndexConfig


class FriendInfo(BaseModel):
    name: str
    link: str
    desc: str


type FriendsConfig = dict[str, list[FriendInfo]]


class ConfigLoader:
    """配置加载器, 负责加载用户定义的配置文件"""

    def __init__(self, source_path: Path) -> None:
        self.source_path = source_path
        self.config_path = source_path / "configs"

    def load_site_config(self) -> SiteConfig | None:
        """加载网站配置"""
        logger.info("正在加载网站配置")

        config_file = self.config_path / "site.toml"
        if not config_file.exists():
            logger.error("加载网站配置失败: 文件不存在")
            return None
        if not config_file.is_file():
            logger.error("加载网站配置失败: site.toml 不是一个文件")
            return None

        try:
            return SiteConfig.model_validate(toml.load(config_file))
        except (ValidationError, toml.TomlDecodeError) as e:
            logger.error(f"加载网站配置失败: {e}")
            return None

    def load_friends_config(self) -> FriendsConfig | None:
        """加载友链配置"""
        logger.info("正在加载友链配置")

        config_file = self.config_path / "friends.toml"
        if not config_file.exists():
            logger.info("配置文件目录下不存在 `friends.toml`, 将不会生成友链页面")
            return None
        if not config_file.is_file():
            logger.warning("加载失败, friends.toml 不是一个文件")
            return None
        # FIXME: 这里要捕获啥异常啊我靠
        return TypeAdapter(FriendsConfig).validate_python(toml.load(config_file))
