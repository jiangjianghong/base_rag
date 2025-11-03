"""
模拟检索策略 - 用于测试
"""
from retriever.registry import retriever_registry
from loguru import logger


@retriever_registry.register("mock")
def mock_retriever(query: str, robot: str = None, strategy_config: dict = None) -> str:
    """
    测试用的模拟检索

    Args:
        query: 用户查询
        robot: 机器人类型
        strategy_config: 策略配置

    Returns:
        模拟的检索结果
    """
    logger.info(f"使用模拟检索策略: robot={robot}")
    return "小明体重99kg，身高1.22m, 是当红明星, 喜欢唱跳rap篮球"
