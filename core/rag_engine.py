"""
统一的RAG引擎
整合LLM、检索器、历史记录管理，提供简洁的API接口
"""
from typing import Union, Generator, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from loguru import logger

from config.config import get_llm_config, get_robot_config
from .rag_builder import RAGChainBuilder
from .history_manager import HistoryManager, get_history_manager


class RAGEngine:
    """
    统一的RAG引擎

    特点：
    - 基于配置自动构建RAG链
    - 支持流式/非流式输出
    - 支持历史记录管理
    - 支持结构化JSON输出
    - 动态检索策略
    """

    def __init__(self):
        """初始化RAG引擎"""
        # 初始化LLM
        llm_config = get_llm_config()
        self.llm = ChatOpenAI(**llm_config)

        # 使用全局单例历史记录管理器
        self.history_manager = get_history_manager()

        logger.info("RAG引擎初始化完成")

    def _merge_config(self, robot_config: Dict[str, Any], runtime_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并配置：运行时配置覆盖机器人默认配置

        Args:
            robot_config: 机器人配置
            runtime_config: 运行时配置（来自API请求）

        Returns:
            合并后的完整配置
        """
        # 获取机器人默认配置
        default_config = robot_config.get('default_config', {})

        # 构建基础配置
        merged = {
            'robot': robot_config['name'],
            'prompt_template': robot_config['prompt_template'],
            'retriever_strategy': robot_config.get('retriever_strategy'),
        }

        # 运行时配置项（优先级：runtime_config > default_config）
        config_keys = ['streaming', 'use_history', 'structured_output', 'temperature', 'max_tokens']
        for key in config_keys:
            if key in runtime_config:
                # 运行时显式指定的配置
                merged[key] = runtime_config[key]
            elif key in default_config:
                # 使用机器人默认配置
                merged[key] = default_config[key]
            else:
                # 使用全局默认值
                defaults = {
                    'streaming': False,
                    'use_history': True,
                    'structured_output': False,
                    'temperature': None,
                    'max_tokens': None
                }
                merged[key] = defaults.get(key)

        logger.debug(f"配置合并完成: {merged}")
        return merged

    def chat(
        self,
        question: str,
        robot: str = "default",
        session_id: Optional[str] = None,
        **runtime_config
    ) -> Union[str, Generator]:
        """
        统一的对话接口

        Args:
            question: 用户问题
            robot: 机器人类型（从config.yaml读取配置）
            session_id: 会话ID（当use_history=True时必需）
            **runtime_config: 运行时配置（可覆盖机器人默认配置）
                - streaming: bool - 是否流式输出
                - use_history: bool - 是否使用历史记录
                - structured_output: bool - 是否JSON结构化输出
                - temperature: float - LLM温度参数
                - max_tokens: int - 最大token数

        Returns:
            Union[str, Generator]:
                - 非流式：返回完整回答字符串
                - 流式：返回生成器

        Raises:
            ValueError: 参数错误或配置错误

        Example:
            # 简单对话（使用机器人默认配置）
            answer = engine.chat("你好", robot="customer_service")

            # 带历史记录的对话
            answer = engine.chat("订单状态", robot="customer_service", session_id="user_123")

            # 覆盖默认配置
            answer = engine.chat(
                "分析数据",
                robot="analyst",
                session_id="session_456",
                streaming=True,
                temperature=0.8
            )
        """
        # 1. 获取机器人配置
        try:
            robot_config = get_robot_config(robot)
        except ValueError as e:
            logger.error(f"获取机器人配置失败: {e}")
            raise

        # 2. 合并配置
        config = self._merge_config(robot_config, runtime_config)

        # 3. 参数验证
        if config['use_history'] and not session_id:
            raise ValueError("使用历史记录时，session_id 参数不能为空")

        # 4. 构建RAG链
        try:
            chain = RAGChainBuilder.build(
                config=config,
                base_llm=self.llm,
                history_manager=self.history_manager if config['use_history'] else None
            )
        except Exception as e:
            logger.error(f"构建RAG链失败: {e}")
            raise

        # 5. 执行推理
        try:
            if config['streaming']:
                # 流式输出
                if config['use_history']:
                    return chain.stream(
                        {"question": question},
                        config={"configurable": {"session_id": session_id}}
                    )
                else:
                    return chain.stream({"question": question})
            else:
                # 非流式输出
                if config['use_history']:
                    return chain.invoke(
                        {"question": question},
                        config={"configurable": {"session_id": session_id}}
                    )
                else:
                    return chain.invoke({"question": question})

        except Exception as e:
            logger.error(f"执行推理失败: {e}")
            raise

    def get_history(self, session_id: str) -> list:
        """
        获取指定会话的历史记录

        Args:
            session_id: 会话ID

        Returns:
            list: 历史消息列表
        """
        return self.history_manager.get_history_messages(session_id)

    def clear_history(self, session_id: str) -> bool:
        """
        清除指定会话的历史记录

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否成功清除
        """
        return self.history_manager.clear_history(session_id)

    def clear_all_history(self) -> int:
        """
        清除所有会话的历史记录

        Returns:
            int: 清除的会话数量
        """
        return self.history_manager.clear_all_history()

    def get_session_info(self) -> Dict[str, Any]:
        """
        获取当前会话统计信息

        Returns:
            Dict[str, Any]: 会话信息，包含总会话数、所有会话ID等
        """
        return {
            'total_sessions': self.history_manager.get_session_count(),
            'session_ids': self.history_manager.get_all_session_ids()
        }


# 创建全局单例实例
_rag_engine_instance: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """
    获取全局RAG引擎实例（单例模式）

    Returns:
        RAGEngine: RAG引擎实例
    """
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance


if __name__ == "__main__":
    # 测试代码
    import sys
    from pathlib import Path

    # 添加项目根目录到路径
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    print("=== 测试RAG引擎 ===\n")

    # 获取引擎实例
    engine = get_rag_engine()
    print(f"✓ RAG引擎初始化成功\n")

    # 测试1：简单对话（不使用历史记录）
    print("测试1: 简单对话")
    try:
        answer = engine.chat(
            "什么是RAG？",
            robot="default",
            use_history=False
        )
        print(f"问题: 什么是RAG？")
        print(f"回答: {answer[:100]}...\n")
    except Exception as e:
        print(f"✗ 失败: {e}\n")

    # 测试2：带历史记录的对话
    print("测试2: 带历史记录的对话")
    try:
        answer1 = engine.chat(
            "你好，我是测试用户",
            robot="default",
            session_id="test_001"
        )
        print(f"第一轮: {answer1[:50]}...")

        answer2 = engine.chat(
            "我刚才说了什么？",
            robot="default",
            session_id="test_001"
        )
        print(f"第二轮: {answer2[:50]}...")

        # 查看历史记录
        history = engine.get_history("test_001")
        print(f"✓ 历史记录条数: {len(history)}\n")
    except Exception as e:
        print(f"✗ 失败: {e}\n")

    # 测试3：会话统计
    print("测试3: 会话统计")
    info = engine.get_session_info()
    print(f"总会话数: {info['total_sessions']}")
    print(f"会话IDs: {info['session_ids']}\n")
