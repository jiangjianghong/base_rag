"""
动态提示词加载器
支持从外部文件动态加载提示词模板
"""
from pathlib import Path
from typing import Dict, Optional
from loguru import logger


class PromptLoader:
    """提示词加载器"""

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        初始化提示词加载器

        Args:
            templates_dir: 提示词模板目录路径，默认为当前文件所在目录下的 templates 文件夹
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"

        self.templates_dir = Path(templates_dir)
        self._cache: Dict[str, str] = {}

        if not self.templates_dir.exists():
            logger.warning(f"提示词模板目录不存在: {self.templates_dir}")
            self.templates_dir.mkdir(parents=True, exist_ok=True)

    def load_prompt(self, name: str, use_cache: bool = True) -> str:
        """
        加载指定名称的提示词模板

        Args:
            name: 提示词模板名称（不含 .md 后缀）
            use_cache: 是否使用缓存，默认为 True

        Returns:
            str: 提示词内容

        Raises:
            ValueError: 当提示词模板不存在时
        """
        # 检查缓存
        if use_cache and name in self._cache:
            return self._cache[name]

        # 构建文件路径
        template_path = self.templates_dir / f"{name}.md"

        if not template_path.exists():
            available_templates = self.list_available_prompts()
            raise ValueError(
                f"提示词模板 '{name}' 不存在。\n"
                f"可用的模板: {', '.join(available_templates)}\n"
                f"请在 {self.templates_dir} 目录下创建 {name}.md 文件"
            )

        try:
            # 读取提示词内容
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # 缓存提示词
            if use_cache:
                self._cache[name] = content

            logger.debug(f"成功加载提示词模板: {name}")
            return content

        except Exception as e:
            logger.error(f"读取提示词模板文件失败: {template_path}, 错误: {e}")
            raise

    def list_available_prompts(self) -> list:
        """
        列出所有可用的提示词模板

        Returns:
            list: 可用的提示词模板名称列表
        """
        if not self.templates_dir.exists():
            return []

        templates = []
        for file_path in self.templates_dir.glob("*.md"):
            templates.append(file_path.stem)

        return sorted(templates)

    def reload_prompt(self, name: str) -> str:
        """
        重新加载指定的提示词模板（清除缓存）

        Args:
            name: 提示词模板名称

        Returns:
            str: 提示词内容
        """
        if name in self._cache:
            del self._cache[name]

        return self.load_prompt(name, use_cache=True)

    def clear_cache(self):
        """清除所有缓存的提示词"""
        self._cache.clear()
        logger.debug("已清除提示词缓存")


# 创建全局实例
_prompt_loader = PromptLoader()


def get_prompt(name: str = "default") -> str:
    """
    获取指定名称的提示词（向后兼容接口）

    Args:
        name: 提示词模板名称

    Returns:
        str: 提示词内容

    Raises:
        ValueError: 当提示词不存在时
    """
    if not isinstance(name, str):
        raise ValueError(f"机器人类型必须是字符串，当前类型: {type(name)}")

    return _prompt_loader.load_prompt(name)


def list_prompts() -> list:
    """列出所有可用的提示词模板"""
    return _prompt_loader.list_available_prompts()


def reload_prompt(name: str) -> str:
    """重新加载提示词（用于热更新）"""
    return _prompt_loader.reload_prompt(name)


if __name__ == "__main__":
    # 测试代码
    print("可用的提示词模板:")
    for prompt_name in list_prompts():
        print(f"  - {prompt_name}")

    print("\n测试加载 default 提示词:")
    try:
        default_prompt = get_prompt("default")
        print(default_prompt[:100] + "...")
    except ValueError as e:
        print(f"错误: {e}")
