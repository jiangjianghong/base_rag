"""
提示词管理模块
支持从外部模板文件动态加载提示词

使用方法:
    from prompt.prompt import get_prompt

    # 加载提示词
    prompt_text = get_prompt("default")

    # 列出所有可用的提示词
    available_prompts = list_prompts()

    # 重新加载提示词（用于热更新）
    reload_prompt("default")
"""
from .prompt_loader import get_prompt, list_prompts, reload_prompt

# 导出公共API
__all__ = ['get_prompt', 'list_prompts', 'reload_prompt']


# 向后兼容的别名（已弃用，仅用于兼容旧代码）
# 新代码请直接使用 get_prompt() 函数
