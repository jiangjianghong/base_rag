"""
Core modules for RAG system
核心模块：RAG引擎、链构建、历史记录管理

主要导出：
- get_rag_engine: 获取全局RAG引擎实例
- RAGEngine: RAG引擎类
- HistoryManager: 历史记录管理器
- get_history_manager: 获取全局历史记录管理器实例
"""

from .rag_engine import RAGEngine, get_rag_engine
from .history_manager import HistoryManager, get_history_manager
from .rag_builder import RAGChainBuilder

__all__ = [
    # RAG引擎
    'RAGEngine',
    'get_rag_engine',

    # 历史记录管理
    'HistoryManager',
    'get_history_manager',

    # 链构建器（高级用法）
    'RAGChainBuilder',
]
