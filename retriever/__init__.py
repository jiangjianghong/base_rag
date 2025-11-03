"""
检索模块 - 负责向量检索和数据库查询

主要导出：
- retriever: 检索函数，根据机器人配置动态选择检索策略
- retriever_registry: 检索策略注册器
"""
from .retriever import retriever
from .registry import retriever_registry

__all__ = ['retriever', 'retriever_registry']
