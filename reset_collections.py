#!/usr/bin/env python3
"""
重置 Milvus 集合工具
用于删除现有集合并重新创建，以更新向量维度
"""

from pymilvus import connections, utility
from config.config import get_milvus_config
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, colorize=True)


def reset_collections():
    """删除并重新创建所有集合"""
    try:
        # 连接到 Milvus
        logger.info("正在连接到 Milvus...")
        milvus_config = get_milvus_config()
        connections.connect(
            alias="default",
            host=milvus_config['host'],
            port=milvus_config['port'],
            user=milvus_config['user'],
            password=milvus_config['password']
        )
        logger.info("✅ Milvus 连接成功")

        # 要删除的集合列表
        collections_to_drop = [
            "history_case_vectors",  # 历史案件向量库
            "qa_vectors"  # 问答向量库 (根据实际名称调整)
        ]

        # 获取所有现有集合
        existing_collections = utility.list_collections()
        logger.info(f"现有集合: {existing_collections}")

        # 删除集合
        for collection_name in collections_to_drop:
            if collection_name in existing_collections:
                logger.warning(f"正在删除集合: {collection_name}")
                utility.drop_collection(collection_name)
                logger.info(f"✅ 已删除集合: {collection_name}")
            else:
                logger.info(f"⚠️ 集合不存在，跳过: {collection_name}")

        logger.info("\n✅ 集合重置完成!")
        logger.info("请重启应用，系统将自动创建新的集合（使用正确的向量维度）")

        # 断开连接
        connections.disconnect("default")

    except Exception as e:
        logger.error(f"❌ 重置失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("⚠️  警告: 此操作将删除所有现有的向量数据!")
    print("="*60)

    response = input("\n确认要继续吗? (输入 'yes' 确认): ")

    if response.lower() == 'yes':
        reset_collections()
    else:
        print("操作已取消")
