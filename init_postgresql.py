#!/usr/bin/env python3
"""
PostgreSQL 数据库初始化脚本
用于创建历史记录表结构
"""
import psycopg
from config.config import get_postgresql_config
from rich.console import Console
from rich.panel import Panel

console = Console()


def init_database():
    """初始化 PostgreSQL 数据库表结构"""
    console.print(Panel.fit("PostgreSQL 数据库初始化", style="bold cyan"))

    try:
        # 获取配置
        pg_config = get_postgresql_config()

        console.print(f"[cyan]连接到数据库: {pg_config['host']}:{pg_config['port']}/{pg_config['database']}[/cyan]")

        # 构建连接字符串
        connection_string = (
            f"postgresql://{pg_config['user']}:{pg_config['password']}"
            f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
        )

        # 建立连接
        connection = psycopg.connect(connection_string)
        connection.autocommit = True

        with connection.cursor() as cursor:
            # 创建 message_store 表
            console.print("\n[yellow]创建 message_store 表...[/yellow]")

            create_table_sql = """
            CREATE TABLE IF NOT EXISTS message_store (
                id SERIAL PRIMARY KEY,
                session_id UUID NOT NULL,
                message JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            cursor.execute(create_table_sql)
            console.print("[green]✓ message_store 表创建成功[/green]")

            # 创建索引
            console.print("\n[yellow]创建索引...[/yellow]")

            create_index_sql = """
            CREATE INDEX IF NOT EXISTS idx_message_store_session_id
            ON message_store(session_id);
            """

            cursor.execute(create_index_sql)
            console.print("[green]✓ session_id 索引创建成功[/green]")

            # 检查表结构
            console.print("\n[yellow]验证表结构...[/yellow]")
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'message_store'
                ORDER BY ordinal_position;
            """)

            columns = cursor.fetchall()
            console.print("[bold]表结构:[/bold]")
            for col_name, col_type in columns:
                console.print(f"  - {col_name}: {col_type}")

        connection.close()

        console.print("\n[bold green]✅ 数据库初始化完成！[/bold green]")
        console.print("\n[cyan]提示：现在可以运行应用程序，历史记录将自动持久化到 PostgreSQL[/cyan]")

    except psycopg.Error as e:
        console.print(f"\n[bold red]❌ 数据库错误: {e}[/bold red]")
        console.print("\n[yellow]请检查：[/yellow]")
        console.print("1. PostgreSQL 服务是否运行")
        console.print("2. config.yaml 中的数据库配置是否正确")
        console.print("3. 数据库用户是否有创建表的权限")
        return False

    except Exception as e:
        console.print(f"\n[bold red]❌ 初始化失败: {e}[/bold red]")
        return False

    return True


def check_database():
    """检查数据库连接和表是否存在"""
    console.print(Panel.fit("检查数据库状态", style="bold cyan"))

    try:
        pg_config = get_postgresql_config()

        # 构建连接字符串
        connection_string = (
            f"postgresql://{pg_config['user']}:{pg_config['password']}"
            f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
        )

        connection = psycopg.connect(connection_string)

        with connection.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'message_store'
                );
            """)
            table_exists = cursor.fetchone()[0]

            if table_exists:
                console.print("[green]✓ message_store 表已存在[/green]")

                # 统计数据
                cursor.execute("SELECT COUNT(*) FROM message_store")
                total_messages = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT session_id) FROM message_store")
                total_sessions = cursor.fetchone()[0]

                console.print(f"\n[bold]当前数据统计:[/bold]")
                console.print(f"  - 总消息数: {total_messages}")
                console.print(f"  - 总会话数: {total_sessions}")
            else:
                console.print("[yellow]⚠ message_store 表不存在[/yellow]")
                console.print("[cyan]请运行初始化命令: python init_postgresql.py init[/cyan]")

        connection.close()

    except Exception as e:
        console.print(f"[bold red]❌ 检查失败: {e}[/bold red]")
        return False

    return True


def drop_table():
    """删除 message_store 表（谨慎使用）"""
    console.print(Panel.fit("删除历史记录表", style="bold red"))
    console.print("[bold red]警告：此操作将删除所有历史记录！[/bold red]\n")

    confirm = input("确认删除？输入 'YES' 继续: ")

    if confirm != "YES":
        console.print("[yellow]操作已取消[/yellow]")
        return False

    try:
        pg_config = get_postgresql_config()

        # 构建连接字符串
        connection_string = (
            f"postgresql://{pg_config['user']}:{pg_config['password']}"
            f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
        )

        connection = psycopg.connect(connection_string)
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS message_store CASCADE;")
            console.print("[green]✓ message_store 表已删除[/green]")

        connection.close()

    except Exception as e:
        console.print(f"[bold red]❌ 删除失败: {e}[/bold red]")
        return False

    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        console.print("[bold cyan]PostgreSQL 初始化工具[/bold cyan]\n")
        console.print("用法:")
        console.print("  python init_postgresql.py init     - 初始化数据库表")
        console.print("  python init_postgresql.py check    - 检查数据库状态")
        console.print("  python init_postgresql.py drop     - 删除表（谨慎使用）")
        sys.exit(0)

    command = sys.argv[1]

    if command == "init":
        init_database()
    elif command == "check":
        check_database()
    elif command == "drop":
        drop_table()
    else:
        console.print(f"[red]未知命令: {command}[/red]")
        sys.exit(1)
