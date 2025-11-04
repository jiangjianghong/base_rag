"""
历史记录管理器
负责管理对话历史记录（使用 PostgreSQL 持久化存储）
"""
from typing import Dict, List, Optional
from langchain_postgres import PostgresChatMessageHistory
from loguru import logger
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


class HistoryManager:
    """历史记录管理器 - 管理所有会话的历史记录（PostgreSQL 持久化）"""

    def __init__(self):
        """初始化历史记录存储 - 使用 PostgreSQL"""
        from config.config import get_postgresql_config

        # 获取 PostgreSQL 配置
        pg_config = get_postgresql_config()

        # 构建连接字符串（用于直接操作数据库）
        self.connection_string = (
            f"postgresql://{pg_config['user']}:{pg_config['password']}"
            f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
        )

        # 保存配置，用于创建连接
        self.pg_config = pg_config
        self.table_name = "message_store"

        # 创建连接池 (min_size=1, max_size=10)
        self.pool = ConnectionPool(
            self.connection_string,
            min_size=1,
            max_size=10,
            open=True
        )

        logger.debug(f"历史记录管理器初始化完成，使用 PostgreSQL: {pg_config['host']}:{pg_config['port']}/{pg_config['database']}")

    def get_session_history(self, session_id: str) -> PostgresChatMessageHistory:
        """
        获取或创建指定会话的历史记录

        Args:
            session_id: 会话ID（UUID 格式）

        Returns:
            PostgresChatMessageHistory: 会话历史记录对象（自动持久化到数据库）
        """
        logger.debug(f"获取会话历史: {session_id}")

        # 从连接池获取连接
        conn = self.pool.getconn()

        # 使用新版 API：位置参数传递 table_name 和 session_id
        return PostgresChatMessageHistory(
            self.table_name,
            session_id,
            sync_connection=conn
        )

    def get_history_messages(self, session_id: str) -> List[dict]:
        """
        获取指定会话的历史消息列表（用于API返回）

        Args:
            session_id: 会话ID

        Returns:
            List[dict]: 历史消息列表，格式为 [{"role": "human/ai", "content": "..."}]
        """
        try:
            history = self.get_session_history(session_id)
            messages = history.messages

            return [
                {
                    "role": msg.type,
                    "content": msg.content
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"获取会话 {session_id} 历史消息失败: {e}")
            return []

    def clear_history(self, session_id: str) -> bool:
        """
        清除指定会话的历史记录

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否成功清除
        """
        try:
            history = self.get_session_history(session_id)
            history.clear()
            logger.info(f"已清除会话历史: {session_id}")
            return True
        except Exception as e:
            logger.error(f"清除会话 {session_id} 历史失败: {e}")
            return False

    def session_exists(self, session_id: str) -> bool:
        """
        检查会话是否存在

        Args:
            session_id: 会话ID

        Returns:
            bool: 会话是否存在（即是否有历史消息）
        """
        try:
            messages = self.get_history_messages(session_id)
            return len(messages) > 0
        except Exception as e:
            logger.error(f"检查会话 {session_id} 是否存在失败: {e}")
            return False

    def get_session_message_count(self, session_id: str) -> int:
        """
        获取指定会话的消息数量

        Args:
            session_id: 会话ID

        Returns:
            int: 消息数量
        """
        try:
            messages = self.get_history_messages(session_id)
            return len(messages)
        except Exception as e:
            logger.error(f"获取会话 {session_id} 消息数量失败: {e}")
            return 0

    def delete_session(self, session_id: str) -> bool:
        """
        删除指定会话（完全移除）

        注意：PostgresChatMessageHistory 使用 clear() 方法清除会话历史

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否成功删除
        """
        return self.clear_history(session_id)

    def clear_all_history(self) -> int:
        """
        清除所有会话的历史记录

        注意：由于使用 PostgreSQL，此操作会直接清空表数据
        需要数据库权限

        Returns:
            int: 清除的会话数量（此实现返回 -1 表示操作完成但无法统计）
        """
        try:
            import psycopg2
            from config.config import get_postgresql_config

            pg_config = get_postgresql_config()

            connection = psycopg2.connect(
                host=pg_config["host"],
                port=pg_config["port"],
                user=pg_config["user"],
                password=pg_config["password"],
                database=pg_config["database"]
            )

            with connection.cursor() as cursor:
                # 统计清除前的会话数
                cursor.execute("SELECT COUNT(DISTINCT session_id) FROM message_store")
                count = cursor.fetchone()[0]

                # 清空表
                cursor.execute("TRUNCATE TABLE message_store")
                connection.commit()

            connection.close()
            logger.info(f"已清除所有会话历史，共 {count} 个会话")
            return count

        except Exception as e:
            logger.error(f"清除所有会话历史失败: {e}")
            return -1

    def get_session_count(self) -> int:
        """
        获取当前会话总数

        Returns:
            int: 会话总数
        """
        try:
            import psycopg2
            from config.config import get_postgresql_config

            pg_config = get_postgresql_config()

            connection = psycopg2.connect(
                host=pg_config["host"],
                port=pg_config["port"],
                user=pg_config["user"],
                password=pg_config["password"],
                database=pg_config["database"]
            )

            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(DISTINCT session_id) FROM message_store")
                count = cursor.fetchone()[0]

            connection.close()
            return count

        except Exception as e:
            logger.error(f"获取会话总数失败: {e}")
            return 0

    def get_all_session_ids(self) -> List[str]:
        """
        获取所有会话ID

        Returns:
            List[str]: 会话ID列表
        """
        try:
            import psycopg2
            from config.config import get_postgresql_config

            pg_config = get_postgresql_config()

            connection = psycopg2.connect(
                host=pg_config["host"],
                port=pg_config["port"],
                user=pg_config["user"],
                password=pg_config["password"],
                database=pg_config["database"]
            )

            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT session_id FROM message_store ORDER BY session_id")
                session_ids = [row[0] for row in cursor.fetchall()]

            connection.close()
            return session_ids

        except Exception as e:
            logger.error(f"获取所有会话ID失败: {e}")
            return []


# 创建全局单例实例
_history_manager_instance: Optional[HistoryManager] = None


def get_history_manager() -> HistoryManager:
    """
    获取全局历史记录管理器实例（单例模式）

    Returns:
        HistoryManager: 历史记录管理器实例
    """
    global _history_manager_instance
    if _history_manager_instance is None:
        _history_manager_instance = HistoryManager()
    return _history_manager_instance


if __name__ == "__main__":
    # 测试代码
    print("=== 测试历史记录管理器（PostgreSQL 版本） ===\n")

    manager = HistoryManager()

    # 测试1: 创建会话
    print("测试1: 创建和获取会话历史")
    history1 = manager.get_session_history("test_session_001")
    history1.add_user_message("你好")
    history1.add_ai_message("你好！有什么可以帮助你的吗？")
    print(f"✓ 会话存在: {manager.session_exists('test_session_001')}")
    print(f"✓ 消息数量: {manager.get_session_message_count('test_session_001')}\n")

    # 测试2: 获取消息列表
    print("测试2: 获取消息列表")
    messages = manager.get_history_messages("test_session_001")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")
    print()

    # 测试3: 多个会话
    print("测试3: 创建多个会话")
    manager.get_session_history("test_session_002")
    manager.get_session_history("test_session_003")
    print(f"✓ 总会话数: {manager.get_session_count()}")
    print(f"✓ 所有会话ID: {manager.get_all_session_ids()}\n")

    # 测试4: 清除单个会话
    print("测试4: 清除单个会话")
    success = manager.clear_history("test_session_001")
    print(f"✓ 清除成功: {success}")
    print(f"✓ 消息数量: {manager.get_session_message_count('test_session_001')}\n")

    print("注意：请手动清理测试数据（test_session_xxx）")
