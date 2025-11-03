"""
问答库向量管理系统
提供问答数据的向量化存储、更新和检索功能
"""

from flask import Blueprint, request, jsonify
from pymilvus import FieldSchema, CollectionSchema, DataType
from vector_manager.base_vector_manager import BaseVectorManager
from loguru import logger
import sys
from typing import List, Dict, Any
from datetime import datetime
import uuid


# 配置日志
logger.remove()
logger.add(sys.stderr, colorize=True)

# 创建蓝图
qa_vector_bp = Blueprint('qa_vector', __name__, url_prefix='/qa_vector')


class QAVectorManager(BaseVectorManager):
    """问答库向量管理器"""

    def __init__(self):
        super().__init__("qa_vectors")

    def get_collection_schema(self) -> CollectionSchema:
        """定义问答库集合的Schema"""
        # 从配置读取向量维度
        if not self.embedding_config:
            self.init_embedding_model()
        vector_dim = self.embedding_config.get('vector_dim', 1536)

        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="qa_id", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="question", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="answer", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="robot_type", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="embedding_question", dtype=DataType.FLOAT_VECTOR, dim=vector_dim),
            FieldSchema(name="embedding_answer", dtype=DataType.FLOAT_VECTOR, dim=vector_dim),
            FieldSchema(name="embedding_all", dtype=DataType.FLOAT_VECTOR, dim=vector_dim),
            FieldSchema(name="create_time", dtype=DataType.INT64),
            FieldSchema(name="is_active", dtype=DataType.BOOL)
        ]

        return CollectionSchema(fields, "问答库向量库")

    def get_index_fields(self) -> List[tuple]:
        """定义需要创建��引的字段"""
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 1024}
        }

        return [
            ("embedding_question", index_params),
            ("embedding_answer", index_params),
            ("embedding_all", index_params)
        ]

    def prepare_entity_data(self, data: Dict[str, Any]) -> tuple:
        """准备问答数据的实体"""
        qa_id = data.get("qa_id")
        question = data.get("question")
        answer = data.get("answer")
        robot_type = data.get("robot_type", "")

        # 验证必填字段
        if not all([qa_id, question, answer]):
            return None, "qa_id", qa_id, {
                "qa_id": qa_id,
                "status": "error",
                "error_msg": "缺少必填字段: qa_id, question, answer"
            }

        # 验证robot_type是否合法（如果提供）
        valid_robot_types = ["ecommerce", "complaint", "introduction", "aftersales", "comprehensive", ""]
        if robot_type and robot_type not in valid_robot_types:
            return None, "qa_id", qa_id, {
                "qa_id": qa_id,
                "status": "error",
                "error_msg": f"robot_type无效，必须是以下之一: {', '.join(valid_robot_types[:-1])}"
            }

        # 生成三个embedding向量
        embedding_question = self.generate_embedding(question)
        embedding_answer = self.generate_embedding(answer)
        embedding_all = self.generate_embedding(f"{question} {answer}")

        # 准备实体数据
        current_time = int(datetime.now().timestamp() * 1000)
        new_id = str(uuid.uuid4())

        entities = [
            [new_id],  # id
            [qa_id],  # qa_id
            [question],  # question
            [answer],  # answer
            [robot_type],  # robot_type
            [embedding_question],  # embedding_question
            [embedding_answer],  # embedding_answer
            [embedding_all],  # embedding_all
            [current_time],  # create_time
            [True]  # is_active
        ]

        return entities, "qa_id", qa_id, None


# 初始化管理器
qa_vector_manager = QAVectorManager()


@qa_vector_bp.route('/upsert', methods=['POST'])
def upsert_qas():
    """
    新增/修改问答接口

    请求体:
    {
        "qas": [
            {
                "qa_id": "xxx",
                "question": "xxx",
                "answer": "xxx",
                "robot_type": "ecommerce"  # 可选: ecommerce/complaint/introduction/aftersales/comprehensive
            }
        ]
    }

    返回:
    {
        "success": true,
        "results": [
            {
                "qa_id": "xxx",
                "status": "add/update/error",
                "error_msg": null or "错误信息"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        qas = data.get("qas", [])

        if not qas or not isinstance(qas, list):
            return jsonify({
                "success": False,
                "message": "请求参数错误: qas字段必须是非空列表"
            }), 400

        # 确保集合已初始化
        if not qa_vector_manager.collection:
            qa_vector_manager.init_collection()

        # 处理每一条问答数据
        results = []
        for qa_data in qas:
            result = qa_vector_manager.upsert_data(qa_data)
            results.append(result)

        return jsonify({
            "success": True,
            "results": results
        })

    except Exception as e:
        logger.error(f"批量处理问答失败: {e}")
        return jsonify({
            "success": False,
            "message": f"处理失败: {str(e)}"
        }), 500


@qa_vector_bp.route('/search', methods=['POST'])
def search_qas():
    """
    搜索问答接口

    请求体:
    {
        "qa_ids": ["xxx", "yyy"],  # 可选,为空则搜索全部
        "query_str": "查询语句",
        "top_k": 10,  # 可选,默认10
        "min_score": 0.5,  # 可选,最低相似度分数
        "robot_type": "ecommerce",  # 可选,场景类型过滤
        "embedding_type": "embedding_question"  # 可选,默认embedding_question, 可选: embedding_question/embedding_answer/embedding_all
    }

    返回:
    {
        "success": true,
        "results": [
            {
                "qa_id": "xxx",
                "question": "xxx",
                "answer": "xxx",
                "score": 0.95
            }
        ]
    }
    """
    try:
        data = request.get_json()
        qa_ids = data.get("qa_ids", [])
        query_str = data.get("query_str")
        top_k = data.get("top_k", 10)
        min_score = data.get("min_score")
        robot_type = data.get("robot_type")
        embedding_type = data.get("embedding_type", "embedding_question")

        if not query_str:
            return jsonify({
                "success": False,
                "message": "query_str参数不能为空"
            }), 400

        # 验证embedding_type
        valid_embedding_types = ["embedding_question", "embedding_answer", "embedding_all"]
        if embedding_type not in valid_embedding_types:
            return jsonify({
                "success": False,
                "message": f"embedding_type无效，必须是以下之一: {', '.join(valid_embedding_types)}"
            }), 400

        # 确保集合已初始化
        if not qa_vector_manager.collection:
            qa_vector_manager.init_collection()

        # 构建过滤表达式
        filter_expr = "is_active == true"

        # 添加qa_ids过滤
        if qa_ids and len(qa_ids) > 0:
            ids_str = '", "'.join(qa_ids)
            filter_expr += f' && qa_id in ["{ids_str}"]'

        # 添加robot_type过滤
        if robot_type:
            filter_expr += f' && robot_type == "{robot_type}"'

        # 执行向量搜索
        results = qa_vector_manager.search_vectors(
            query_text=query_str,
            vector_field=embedding_type,
            filter_expr=filter_expr,
            top_k=top_k,
            min_score=min_score,
            output_fields=["qa_id", "question", "answer"]
        )

        logger.info(f"搜索完成,返回{len(results)}条结果")

        return jsonify({
            "success": True,
            "results": results
        })

    except Exception as e:
        logger.error(f"搜索问答失败: {e}")
        return jsonify({
            "success": False,
            "message": f"搜索失败: {str(e)}"
        }), 500


@qa_vector_bp.route('/init', methods=['POST'])
def init_collection():
    """初始化集合接口"""
    try:
        qa_vector_manager.init_collection()
        qa_vector_manager.init_embedding_model()
        return jsonify({
            "success": True,
            "message": "集合初始化成功"
        })
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        return jsonify({
            "success": False,
            "message": f"初始化失败: {str(e)}"
        }), 500


# 应用启动时初始化
try:
    qa_vector_manager.init_collection()
    qa_vector_manager.init_embedding_model()
    logger.info("问答库向量系统初始化完成")
except Exception as e:
    logger.error(f"系统初始化失败: {e}")
