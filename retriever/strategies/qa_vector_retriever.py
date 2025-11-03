"""
QA向量检索策略 - 使用QAVectorManager进行向量检索
"""
from retriever.registry import retriever_registry
from loguru import logger


@retriever_registry.register("qa_vector")
def qa_vector_retriever(query: str, robot: str, strategy_config: dict) -> str:
    """
    使用QAVectorManager进行向量检索

    Args:
        query: 用户查询
        robot: 机器人类型
        strategy_config: 检索策略配置

    Returns:
        格式化的问答结果文本
    """
    try:
        from QAVectorManager.QAVectorManager import qa_vector_manager

        # 从策略配置中读取参数
        params = strategy_config.get('params', {})
        top_k = params.get('top_k', 5)
        min_score = params.get('min_score')
        embedding_type = params.get('embedding_type', 'embedding_all')
        metric_type = params.get('metric_type', 'COSINE')
        nprobe = params.get('nprobe', 10)

        logger.info(f"检索配置[{robot}]: top_k={top_k}, embedding_type={embedding_type}, metric_type={metric_type}, min_score={min_score}")

        # 确保集合已初始化
        if not qa_vector_manager.collection:
            qa_vector_manager.init_collection()

        # 生成查询向量
        query_embedding = qa_vector_manager.generate_embedding(query)

        # 定义搜索参数
        search_params = {
            "metric_type": metric_type,
            "params": {"nprobe": nprobe}
        }

        # 构建过滤表达式
        filter_expr = f'is_active == true && robot_type == "{robot}"'

        # 执行向量搜索
        search_results = qa_vector_manager.collection.search(
            data=[query_embedding],
            anns_field=embedding_type,
            param=search_params,
            limit=top_k,
            expr=filter_expr,
            output_fields=["question", "answer", "qa_id"]
        )

        # 格式化返回结果
        return_results = []
        for hits in search_results:
            for hit in hits:
                score = hit.score

                # 如果设置了最低分数阈值,过滤低分结果
                if min_score is not None and score < min_score:
                    continue

                question = hit.entity.get("question", "")
                answer = hit.entity.get("answer", "")
                # 格式化为问答对形式
                return_results.append(f"Q: {question}\nA: {answer}")

        if not return_results:
            logger.warning(f"未找到匹配的问答数据: robot_type={robot}")
            return ""

        logger.info(f"检索成功,返回 {len(return_results)} 条结果")
        return "\n\n".join(return_results)

    except Exception as e:
        logger.error(f"检索失败: {e}")
        return ""
