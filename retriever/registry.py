"""
检索函数注册器
提供简单的装饰器和注册机制，方便用户快速添加自定义检索函数
"""
from typing import Callable, Dict, Any
from loguru import logger


class RetrieverRegistry:
    """检索函数注册器"""

    def __init__(self):
        self._retrievers: Dict[str, Callable] = {}

    def register(self, strategy_type: str):
        """
        装饰器：注册检索函数

        使用方法:
            @retriever_registry.register("my_custom_retriever")
            def my_retriever(query: str, robot: str, strategy_config: dict) -> str:
                # 自定义检索逻辑
                return "检索结果"

        Args:
            strategy_type: 检索策略类型（与 config.yaml 中的 type 字段对应）
        """
        def decorator(func: Callable):
            self._retrievers[strategy_type] = func
            logger.info(f"已注册检索函数: {strategy_type} -> {func.__name__}")
            return func
        return decorator

    def register_function(self, strategy_type: str, func: Callable):
        """
        直接注册检索函数（不使用装饰器）

        Args:
            strategy_type: 检索策略类型
            func: 检索函数
        """
        self._retrievers[strategy_type] = func
        logger.info(f"已注册检索函数: {strategy_type} -> {func.__name__}")

    def get(self, strategy_type: str) -> Callable:
        """
        获取注册的检索函数

        Args:
            strategy_type: 检索策略类型

        Returns:
            检索函数

        Raises:
            KeyError: 当检索策略类型不存在时
        """
        if strategy_type not in self._retrievers:
            available = ", ".join(self._retrievers.keys())
            raise KeyError(
                f"检索策略类型 '{strategy_type}' 未注册。\n"
                f"可用的策略类型: {available if available else '(无)'}"
            )
        return self._retrievers[strategy_type]

    def list_all(self) -> Dict[str, str]:
        """
        列出所有注册的检索函数

        Returns:
            字典：策略类型 -> 函数名
        """
        return {
            strategy_type: func.__name__
            for strategy_type, func in self._retrievers.items()
        }

    def exists(self, strategy_type: str) -> bool:
        """
        检查检索策略是否已注册

        Args:
            strategy_type: 检索策略类型

        Returns:
            True 如果已注册，否则 False
        """
        return strategy_type in self._retrievers


# 全局注册器实例
retriever_registry = RetrieverRegistry()
