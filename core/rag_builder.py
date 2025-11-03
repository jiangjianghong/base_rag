"""
RAG链构建器
统一构建RAG处理链，消除代码重复
"""
from typing import Dict, Any, Callable, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from loguru import logger

from prompt.prompt import get_prompt
from retriever.retriever import retriever
from .history_manager import HistoryManager


class RAGChainBuilder:
    """RAG链构建器 - 统一构建逻辑"""

    @staticmethod
    def build_prompt_template(config: Dict[str, Any]) -> str:
        """
        构建提示词模板

        Args:
            config: 运行时配置

        Returns:
            str: 完整的提示词模板
        """
        # 获取基础提示词
        prompt_template = get_prompt(config['prompt_template'])

        # 添加检索上下文占位符
        prompt = prompt_template + "\n\n知识库相关检索结果：{context}"

        # 如果需要结构化输出，添加JSON格式要求
        if config.get('structured_output'):
            prompt += "\n\n重要：请严格按照JSON格式返回结果。你的回答必须是一个有效的JSON对象，不要包含任何其他解释性文字。"

        return prompt

    @staticmethod
    def build_llm(config: Dict[str, Any], base_llm: ChatOpenAI) -> ChatOpenAI:
        """
        构建LLM实例（如果配置中指定了temperature则创建新实例）

        Args:
            config: 运行时配置
            base_llm: 基础LLM实例

        Returns:
            ChatOpenAI: LLM实例
        """
        temperature = config.get('temperature')

        # 如果没有指定temperature或与默认值相同，直接使用base_llm
        if temperature is None or temperature == base_llm.temperature:
            return base_llm

        # 创建新的LLM实例
        from config.config import get_llm_config
        llm_config = get_llm_config()
        llm_config['temperature'] = temperature

        logger.debug(f"创建新LLM实例，temperature={temperature}")
        return ChatOpenAI(**llm_config)

    @staticmethod
    def build_retriever_func(config: Dict[str, Any]) -> Callable:
        """
        构建检索函数

        Args:
            config: 运行时配置

        Returns:
            Callable: 检索函数，签名为 (query: str) -> str
        """
        robot = config['robot']

        # 返回一个闭包，捕获robot参数
        def retrieve_func(query: str) -> str:
            return retriever(query, robot=robot)

        return retrieve_func

    @staticmethod
    def build_chain_with_history(
        config: Dict[str, Any],
        llm: ChatOpenAI,
        retrieve_func: Callable,
        history_manager: HistoryManager
    ) -> RunnableWithMessageHistory:
        """
        构建带历史记录的RAG链

        Args:
            config: 运行时配置
            llm: LLM实例
            retrieve_func: 检索函数
            history_manager: 历史记录管理器

        Returns:
            RunnableWithMessageHistory: 带历史记录的RAG链
        """
        # 构建提示词模板
        sys_prompt = RAGChainBuilder.build_prompt_template(config)

        # 创建带历史记录占位符的提示词
        prompt = ChatPromptTemplate.from_messages([
            ("system", sys_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])

        # 构建基础链
        base_chain = (
            {
                "context": lambda x: retrieve_func(x["question"]),
                "question": lambda x: x["question"],
                "chat_history": lambda x: x.get("chat_history", [])
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        # 包装为带历史记录的链
        chain = RunnableWithMessageHistory(
            base_chain,
            history_manager.get_session_history,
            input_messages_key="question",
            history_messages_key="chat_history"
        )

        logger.debug(f"构建带历史记录的RAG链: robot={config['robot']}")
        return chain

    @staticmethod
    def build_chain_without_history(
        config: Dict[str, Any],
        llm: ChatOpenAI,
        retrieve_func: Callable
    ) -> Runnable:
        """
        构建不带历史记录的RAG链（单次对话）

        Args:
            config: 运行时配置
            llm: LLM实例
            retrieve_func: 检索函数

        Returns:
            Runnable: RAG链
        """
        # 构建提示词模板
        sys_prompt = RAGChainBuilder.build_prompt_template(config)

        # 创建提示词
        prompt = ChatPromptTemplate.from_messages([
            ("system", sys_prompt),
            ("human", "{question}")
        ])

        # 构建链
        chain = (
            {
                "context": lambda x: retrieve_func(x["question"]),
                "question": lambda x: x["question"]
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        logger.debug(f"构建不带历史记录的RAG链: robot={config['robot']}, structured_output={config.get('structured_output')}")
        return chain

    @staticmethod
    def build(
        config: Dict[str, Any],
        base_llm: ChatOpenAI,
        history_manager: Optional[HistoryManager] = None
    ) -> Runnable:
        """
        统一入口：根据配置自动选择构建带/不带历史记录的链

        Args:
            config: 运行时配置
            base_llm: 基础LLM实例
            history_manager: 历史记录管理器（当use_history=True时必需）

        Returns:
            Runnable: RAG链（可能是RunnableWithMessageHistory或普通Runnable）

        Raises:
            ValueError: 当use_history=True但未提供history_manager时
        """
        # 验证参数
        if config.get('use_history') and history_manager is None:
            raise ValueError("use_history=True时必须提供history_manager")

        # 构建LLM
        llm = RAGChainBuilder.build_llm(config, base_llm)

        # 构建检索函数
        retrieve_func = RAGChainBuilder.build_retriever_func(config)

        # 根据配置选择构建方式
        if config.get('use_history'):
            return RAGChainBuilder.build_chain_with_history(
                config, llm, retrieve_func, history_manager
            )
        else:
            return RAGChainBuilder.build_chain_without_history(
                config, llm, retrieve_func
            )


if __name__ == "__main__":
    # 测试代码
    import sys
    from pathlib import Path

    # 添加项目根目录到路径
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from config.config import get_llm_config
    from .history_manager import get_history_manager

    print("=== 测试RAG链构建器 ===\n")

    # 初始化LLM
    llm_config = get_llm_config()
    llm = ChatOpenAI(**llm_config)

    # 初始化历史记录管理器
    history_mgr = get_history_manager()

    # 测试1: 构建不带历史记录的链
    print("测试1: 构建不带历史记录的链")
    config1 = {
        'robot': 'default',
        'prompt_template': 'default',
        'use_history': False,
        'structured_output': False,
        'temperature': None
    }
    try:
        chain1 = RAGChainBuilder.build(config1, llm)
        print(f"✓ 成功构建: {type(chain1).__name__}\n")
    except Exception as e:
        print(f"✗ 失败: {e}\n")

    # 测试2: 构建带历史记录的链
    print("测试2: 构建带历史记录的链")
    config2 = {
        'robot': 'default',
        'prompt_template': 'default',
        'use_history': True,
        'structured_output': False,
        'temperature': None
    }
    try:
        chain2 = RAGChainBuilder.build(config2, llm, history_mgr)
        print(f"✓ 成功构建: {type(chain2).__name__}\n")
    except Exception as e:
        print(f"✗ 失败: {e}\n")

    # 测试3: 使用自定义temperature
    print("测试3: 使用自定义temperature")
    config3 = {
        'robot': 'default',
        'prompt_template': 'default',
        'use_history': False,
        'structured_output': False,
        'temperature': 0.8
    }
    try:
        chain3 = RAGChainBuilder.build(config3, llm)
        print(f"✓ 成功构建\n")
    except Exception as e:
        print(f"✗ 失败: {e}\n")
