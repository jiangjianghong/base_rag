"""
统一向量管理器基类
提供通用的向量存储、检索和管理功能
"""
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from config.config import get_milvus_config, get_embedding_config
from loguru import logger
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
import uuid
import requests


# 配置日志
logger.remove()
logger.add(sys.stderr, colorize=True)


class BaseVectorManager(ABC):
    """向量管理器基类"""

    def __init__(self, collection_name: str):
        """
        初始化向量管理器

        Args:
            collection_name: Milvus 集合名称
        """
        self.collection_name = collection_name
        self.milvus_connected = False
        self.collection = None
        self.embedding_config = None

    def connect_milvus(self):
        """连接Milvus向量数据库"""
        try:
            if not self.milvus_connected:
                milvus_config = get_milvus_config()
                connections.connect(
                    alias="default",
                    host=milvus_config['host'],
                    port=milvus_config['port'],
                    user=milvus_config['user'],
                    password=milvus_config['password']
                )
                self.milvus_connected = True
                # logger.debug("Milvus连接成功")
        except Exception as e:
            logger.error(f"Milvus连接失败: {e}")
            raise

    def init_embedding_model(self):
        """初始化Embedding配置"""
        try:
            self.embedding_config = get_embedding_config()
            # logger.debug("Embedding配置加载成功")
        except Exception as e:
            logger.error(f"Embedding配置加载失败: {e}")
            raise

    @abstractmethod
    def get_collection_schema(self) -> CollectionSchema:
        """
        获取集合的Schema定义（子类必须实现）

        Returns:
            CollectionSchema: 集合的Schema
        """
        pass

    @abstractmethod
    def get_index_fields(self) -> List[tuple]:
        """
        获取需要创建索引的字段（子类必须实现）

        Returns:
            List[tuple]: 索引字段列表，每个元素为 (field_name, index_params) 的元组
        """
        pass

    def init_collection(self):
        """初始化Milvus集合"""
        try:
            self.connect_milvus()

            # 检查集合是否存在
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                self.collection.load()
                # logger.debug(f"加载现有集合: {self.collection_name}")
            else:
                # 创建新集合
                if not self.embedding_config:
                    self.init_embedding_model()

                schema = self.get_collection_schema()
                self.collection = Collection(self.collection_name, schema)

                # 创建索引
                for field_name, index_params in self.get_index_fields():
                    self.collection.create_index(field_name, index_params)

                logger.info(f"集合不存在，创建新集合: {self.collection_name}")

            # 确保集合已加载
            self.collection.load()
            return self.collection

        except Exception as e:
            logger.error(f"初始化Milvus集合失败: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """生成文本的embedding向量，支持OpenAI和TEI两种格式"""
        try:
            if not self.embedding_config:
                self.init_embedding_model()

            # 获取embedding类型，默认为openai
            embedding_type = self.embedding_config.get('type', 'openai')

            if embedding_type == 'tei':
                # 原生TEI格式
                url = self.embedding_config['base_url']
                # 如果base_url不包含/embed，则添加
                if not url.endswith('/embed'):
                    url = f"{url}/embed"

                headers = {"Content-Type": "application/json"}
                payload = {"inputs": [text]}

                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()

                result = response.json()
                # TEI可能直接返回list，或者返回{"data": [{"embedding": [...]}]}
                if isinstance(result, list):
                    embedding = result[0]
                else:
                    embedding = result['data'][0]['embedding']

            else:
                # OpenAI兼容格式（默认）
                url = f"{self.embedding_config['base_url']}/embeddings"
                headers = {
                    "Authorization": f"Bearer {self.embedding_config['api_key']}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.embedding_config['model'],
                    "input": text
                }

                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()

                result = response.json()
                embedding = result['data'][0]['embedding']

            return embedding
        except Exception as e:
            logger.error(f"生成embedding失败: {e}")
            raise

    def check_exists(self, field_name: str, field_value: str) -> Optional[str]:
        """
        检查指定字段的值是否已存在，返回对应的主键id

        Args:
            field_name: 字段名称
            field_value: 字段值

        Returns:
            Optional[str]: 存在时返回主键id，否则返回None
        """
        try:
            expr = f'{field_name} == "{field_value}" && is_active == true'
            results = self.collection.query(
                expr=expr,
                output_fields=["id"]
            )

            if results and len(results) > 0:
                return results[0]["id"]
            return None
        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            return None

    @abstractmethod
    def prepare_entity_data(self, data: Dict[str, Any]) -> tuple:
        """
        准备插入实体的数据（子类必须实现）

        Args:
            data: 原始数据字典

        Returns:
            tuple: (entities列表, unique_field, unique_value, status)
                - entities: 准备插入的实体列表
                - unique_field: 唯一字段名称
                - unique_value: 唯一字段值
                - status: 操作状态（add/update）
        """
        pass

    def upsert_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        插入或更新数据的通用方法

        Args:
            data: 数据字典

        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            # 调用子类实现的方法准备数据
            entities, unique_field, unique_value, validation_error = self.prepare_entity_data(data)

            # 如果有验证错误，直接返回
            if validation_error:
                return validation_error

            # 检查是否已存在
            existing_id = self.check_exists(unique_field, unique_value)

            if existing_id:
                # 更新操作:先删除旧数据
                delete_expr = f'id == "{existing_id}"'
                self.collection.delete(delete_expr)
                status = "update"
                logger.info(f"删除旧数据: {existing_id}")
            else:
                status = "add"

            # 插入新数据
            self.collection.insert(entities)
            self.collection.flush()

            logger.info(f"数据{status}成功: {unique_value}")

            return {
                unique_field: unique_value,
                "status": status,
                "error_msg": None
            }

        except Exception as e:
            error_msg = f"处理数据失败: {str(e)}"
            logger.error(error_msg)
            return {
                unique_field: data.get(unique_field),
                "status": "error",
                "error_msg": error_msg
            }

    def search_vectors(
        self,
        query_text: str,
        vector_field: str,
        filter_expr: str = "is_active == true",
        top_k: int = 10,
        min_score: Optional[float] = None,
        output_fields: Optional[List[str]] = None,
        metric_type: str = "COSINE",
        nprobe: int = 10
    ) -> List[Dict[str, Any]]:
        """
        通用向量搜索方法

        Args:
            query_text: 查询文本
            vector_field: 向量字段名称
            filter_expr: 过滤表达式
            top_k: 返回结果数量
            min_score: 最低相似度分数
            output_fields: 输出字段列表
            metric_type: 相似度度量类型
            nprobe: 搜索参数

        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        try:
            # 生成查询向量
            query_embedding = self.generate_embedding(query_text)

            # 定义搜索参数
            search_params = {
                "metric_type": metric_type,
                "params": {"nprobe": nprobe}
            }

            # 执行向量搜索
            search_results = self.collection.search(
                data=[query_embedding],
                anns_field=vector_field,
                param=search_params,
                limit=top_k,
                expr=filter_expr,
                output_fields=output_fields or []
            )

            # 处理搜索结果
            results = []
            for hits in search_results:
                for hit in hits:
                    score = hit.score

                    # 过滤低于最低分数的结果
                    if min_score is not None and score < min_score:
                        continue

                    result = {"score": float(score)}
                    for field in output_fields or []:
                        result[field] = hit.entity.get(field)

                    results.append(result)

            logger.info(f"搜索完成,返回{len(results)}条结果")
            return results

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
