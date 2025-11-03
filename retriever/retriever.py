"""
检索模块 - 负责向量检索和数据库查询
使用动态配置的检索策略，支持灵活扩展

添加新的检索策略只需两步：
1. 在 retriever/strategies/ 目录下创建新文件
2. 使用 @retriever_registry.register("策略类型") 装饰器定义检索函数
3. 在 config.yaml 的 retriever_strategies 中添加对应配置

示例：
    # retriever/strategies/my_strategy.py
    from retriever.registry import retriever_registry

    @retriever_registry.register("my_strategy")
    def my_custom_retriever(query: str, robot: str, strategy_config: dict) -> str:
        # 自定义检索逻辑
        return "检索结果"
"""
from loguru import logger
from config.config import get_robot_config, get_retriever_strategies_config
from .registry import retriever_registry

# 自动导入所有检索策略实现
from .strategies import mock_retriever, qa_vector_retriever


def retriever(query: str, robot: str = "default") -> str:
    """
    检索函数 - 根据机器人配置动态选择检索策略

    Args:
        query: 用户的问题
        robot: 机器人类型，从配置文件读取

    Returns:
        str: 检索到的上下文本
    """
    try:
        # 获取机器人配置
        robot_config = get_robot_config(robot)
        retriever_strategy = robot_config.get('retriever_strategy')

        # 如果没有配置检索策略，返回空字符串
        if not retriever_strategy:
            logger.debug(f"机器人 '{robot}' 未配置检索策略，跳过检索")
            return ""

        # 获取检索策略配置
        strategies_config = get_retriever_strategies_config()
        strategy_config = strategies_config.get(retriever_strategy)

        if not strategy_config:
            logger.warning(f"检索策略 '{retriever_strategy}' 未在配置中定义")
            return ""

        # 根据策略类型从注册器获取检索函数
        strategy_type = strategy_config.get('type')

        if not strategy_type:
            logger.warning(f"检索策略 '{retriever_strategy}' 未定义 type 字段")
            return ""

        try:
            # 从注册器获取检索函数
            retriever_func = retriever_registry.get(strategy_type)
            # 调用检索函数
            return retriever_func(query, robot, strategy_config)
        except KeyError as e:
            logger.error(f"检索策略类型 '{strategy_type}' 未注册: {e}")
            return ""

    except ValueError as e:
        # 机器人不存在或未启用
        logger.error(f"检索失败: {e}")
        raise
    except Exception as e:
        logger.error(f"检索过程发生错误: {e}")
        return ""


if __name__ == "__main__":
    # 添加项目根目录到 Python 路径 (仅在直接运行本文件时需要)
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 测试检索函数
    test_query = "如何退货退款"
    result = retriever(test_query, robot="ecommerce")
    print("检索结果:\n", result)
