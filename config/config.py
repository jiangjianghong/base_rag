"""
配置文件读取模块
从 config.yaml 读取项目配置，支持环境变量替换
"""
import yaml
import os
import sys
import time
import requests
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

# 尝试导入 python-dotenv，如果可用则自动加载 .env 文件
try:
    from dotenv import load_dotenv
    # 自动加载 .env 文件
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # 如果没有安装 python-dotenv，静默忽略
    pass

console = Console()


def get_config_path() -> Path:
    """获取配置文件路径"""
    # 获取项目根目录（config 文件夹的上一级）
    current_dir = Path(__file__).parent.parent
    config_path = current_dir / "config.yaml"
    return config_path


def load_config() -> Dict[str, Any]:
    """
    加载配置文件
    
    Returns:
        Dict[str, Any]: 配置字典
    
    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML 格式错误
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_llm_config() -> Dict[str, Any]:
    """
    获取 LLM 模型配置
    
    Returns:
        Dict[str, Any]: LLM 配置字典，包含 api_key, base_url, model, temperature, max_tokens 等
    """
    config = load_config()
    llm_config = config.get('llm', {})
    
    # 优先从环境变量读取 API Key
    api_key = os.environ.get('OPENAI_API_KEY') or llm_config.get('api_key')
    
    if not api_key or api_key == "your-api-key-here":
        raise ValueError("请在 config.yaml 的 llm 部分设置 api_key")
    
    # 返回完整配置
    result = {
        'api_key': api_key,
        'base_url': llm_config.get('base_url'),
        'model': llm_config.get('model', 'gpt-3.5-turbo'),
        'temperature': llm_config.get('temperature', 0),
        'max_tokens': llm_config.get('max_tokens', 2000)
    }
    
    # 添加可选参数（如果存在）
    if 'extra_body' in llm_config:
        result['extra_body'] = llm_config['extra_body']
    
    return result


def get_embedding_config() -> Dict[str, Any]:
    """
    获取 Embedding 模型配置
    
    Returns:
        Dict[str, Any]: Embedding 配置字典，包含 api_key, base_url, model 等
    """
    config = load_config()
    embedding_config = config.get('embedding', {})
    
    # 优先从环境变量读取 API Key
    api_key = os.environ.get('OPENAI_API_KEY') or embedding_config.get('api_key')
    
    if not api_key or api_key == "your-api-key-here":
        raise ValueError("请在 config.yaml 的 embedding 部分设置 api_key 或在环境变量中设置 OPENAI_API_KEY")
    
    # 返回完整配置
    return {
        'api_key': api_key,
        'base_url': embedding_config.get('base_url'),
        'model': embedding_config.get('model', 'text-embedding-ada-002'),
        'type': embedding_config.get('type', 'openai'),  # 默认openai格式
        'vector_dim': embedding_config.get('vector_dim', 1536)  # 默认1536维
    }


def get_milvus_config() -> Dict[str, Any]:
    """
    获取 Milvus 配置
    
    Returns:
        Dict[str, Any]: Milvus 配置字典，包含 host, port, user, password 等
    """
    config = load_config()
    milvus_config = config.get('milvus', {})
    
    if not milvus_config:
        raise ValueError("请在 config.yaml 中配置 milvus 部分")
    
    return {
        'host': milvus_config.get('host', 'localhost'),
        'port': milvus_config.get('port', 19530),
        'user': milvus_config.get('user', ''),
        'password': milvus_config.get('password', '')
    }


def get_postgresql_config() -> Dict[str, Any]:
    """
    获取 PostgreSQL 配置

    Returns:
        Dict[str, Any]: PostgreSQL 配置字典，包含 host, port, user, password, database, schema 等
    """
    config = load_config()
    pg_config = config.get('postgresql', {})

    if not pg_config:
        raise ValueError("请在 config.yaml 中配置 postgresql 部分")

    return {
        'host': pg_config.get('host', 'localhost'),
        'port': pg_config.get('port', 5432),
        'user': pg_config.get('user', 'postgres'),
        'password': pg_config.get('password', ''),
        'database': pg_config.get('database', ''),
        'schema': pg_config.get('schema', 'public')
    }


def get_retriever_config(method: str = "robot") -> Dict[str, Any]:
    """
    获取检索配置
    
    Args:
        method: 检索方法名称 (robot/case/等)，默认为 robot
    
    Returns:
        Dict[str, Any]: 检索配置字典，包含 top_k, min_score, embedding_type, metric_type, nprobe 等
    """
    config = load_config()
    retriever_config = config.get('retriever', {})
    method_config = retriever_config.get(method, {})
    
    # 如果指定方法没有配置，返回默认值
    return {
        'top_k': method_config.get('top_k', 5),
        'min_score': method_config.get('min_score'),  # 可选，默认为 None
        'embedding_type': method_config.get('embedding_type', 'embedding_all'),
        'metric_type': method_config.get('metric_type', 'COSINE'),
        'nprobe': method_config.get('nprobe', 10)
    }


def get_all_config() -> Dict[str, Any]:
    """
    获取所有配置

    Returns:
        Dict[str, Any]: 完整的配置字典
    """
    return load_config()


def get_robots_config() -> list:
    """
    获取机器人配置列表

    Returns:
        list: 机器人配置列表，每个元素包含 name, description, prompt_template, retriever_strategy, enabled
    """
    config = load_config()
    return config.get('robots', [])


def get_robot_config(robot_name: str) -> Dict[str, Any]:
    """
    获取指定机器人的配置

    Args:
        robot_name: 机器人名称

    Returns:
        Dict[str, Any]: 机器人配置字典

    Raises:
        ValueError: 当机器人不存在或未启用时
    """
    robots = get_robots_config()

    for robot in robots:
        if robot.get('name') == robot_name:
            if not robot.get('enabled', True):
                raise ValueError(f"机器人 '{robot_name}' 已禁用")
            return robot

    # 机器人不存在，列出可用的机器人
    available_robots = [r['name'] for r in robots if r.get('enabled', True)]
    raise ValueError(
        f"机器人 '{robot_name}' 不存在。\n"
        f"可用的机器人: {', '.join(available_robots)}"
    )


def list_available_robots() -> list:
    """
    列出所有可用（已启用）的机器人

    Returns:
        list: 机器人名称列表
    """
    robots = get_robots_config()
    return [r['name'] for r in robots if r.get('enabled', True)]


def get_retriever_strategies_config() -> Dict[str, Any]:
    """
    获取检索策略配置

    Returns:
        Dict[str, Any]: 检索策略配置字典
    """
    config = load_config()
    return config.get('retriever_strategies', {})


def print_all_config():
    console.print("[bold cyan]应用配置信息[/bold cyan]")
    sections = [
        ("LLM 配置", get_llm_config),
        ("Embedding 配置", get_embedding_config),
        ("Milvus 配置", get_milvus_config),
        ("PostgreSQL 配置", get_postgresql_config),
    ]

    for title, getter in sections:
        try:
            cfg = getter()
            # 构造表格
            table = Table(show_lines=True, box=None)
            table.add_column("键", style="bold green", width=20)
            table.add_column("值", style="white")

            for k, v in cfg.items():
                table.add_row(k, str(v))

            # 打印表格 panel
            console.print(Panel(table, title=title, border_style="cyan"))
            sys.stdout.flush() 
            time.sleep(0.3)      
        except Exception as e:
            console.print(f"[red]❌ {title} 加载失败: {e}[/red]")
            sys.stdout.flush()
            time.sleep(0.2)

def test_config(name: str):
    """
    通用配置测试函数，支持以下测试类型：
    - llm: 测试 LLM API 连通性
    - embedding: 测试 Embedding API 连通性
    - milvus: 测试 Milvus 向量数据库连通性
    - postgresql: 测试 PostgreSQL 数据库连通性

    Args:
        name: 要测试的配置名称 ('llm', 'embedding', 'milvus', 'postgresql')
    """

    if name == "llm":
        llm_config = get_llm_config()
        console.print("[bold cyan]开始测试 LLM 连通性...[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("初始化配置...", total=5)

            # 1. 初始化
            time.sleep(0.5)
            progress.advance(task)

            # 2. 检查 URL
            base_url = llm_config["base_url"]
            if not base_url.startswith("http"):
                console.print(f"[red]❌ 无效的 Base URL: {base_url}[/red]")
                return
            progress.update(task, description="验证 Base URL...")
            time.sleep(0.5)
            progress.advance(task)

            # 3. 构建请求
            headers = {
                "Authorization": f"Bearer {llm_config['api_key']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": llm_config["model"],
                "messages": [{"role": "user", "content": "你好，测试连接"}],
                "max_tokens": 20,
                "temperature": llm_config["temperature"]
            }
            # 注意 extra_body 可能是 dict
            if "extra_body" in llm_config and isinstance(llm_config["extra_body"], dict):
                data.update(llm_config["extra_body"])

            progress.update(task, description="发送测试请求...")
            time.sleep(0.5)
            progress.advance(task)

            # 4. 发送请求
            try:
                resp = requests.post(f"{base_url}/chat/completions",
                                     headers=headers, json=data, timeout=10)
            except requests.exceptions.RequestException as e:
                console.print(f"[red]❌ 连接失败: {e}[/red]")
                return

            progress.update(task, description="解析响应中...")
            time.sleep(0.5)
            progress.advance(task)

            # 5. 结果分析
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    msg = result["choices"][0]["message"]["content"]
                    progress.update(task, description="✅ 测试成功")
                    progress.advance(task)
                    console.print(f"[green]✅ LLM 连接正常[/green]")
                    console.print(f"[bold]返回示例：[/bold] {msg}")
                except Exception as e:
                    console.print(f"[yellow]⚠️ 响应解析失败: {e}[/yellow]")
            else:
                console.print(f"[red]❌ 请求失败，状态码: {resp.status_code}[/red]")
                console.print(resp.text)
    
    elif name == "embedding":
        embedding_config = get_embedding_config()
        embedding_type = embedding_config.get('type', 'openai')
        console.print(f"[bold cyan]开始测试 Embedding 连通性 (类型: {embedding_type})...[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("初始化配置...", total=5)

            # 1. 初始化
            time.sleep(0.5)
            progress.advance(task)

            # 2. 检查 URL
            base_url = embedding_config["base_url"]
            if not base_url.startswith("http"):
                console.print(f"[red]❌ 无效的 Base URL: {base_url}[/red]")
                return
            progress.update(task, description="验证 Base URL...")
            time.sleep(0.5)
            progress.advance(task)

            # 3. 根据类型构建请求
            progress.update(task, description="发送测试请求...")
            time.sleep(0.5)
            progress.advance(task)

            # 4. 发送请求
            try:
                if embedding_type == 'tei':
                    # TEI原生格式
                    url = base_url if base_url.endswith('/embed') else f"{base_url}/embed"
                    headers = {"Content-Type": "application/json"}
                    data = {"inputs": ["测试连接性"]}
                    resp = requests.post(url, headers=headers, json=data, timeout=10)
                else:
                    # OpenAI兼容格式
                    headers = {
                        "Authorization": f"Bearer {embedding_config['api_key']}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": embedding_config["model"],
                        "input": "测试连接性"
                    }
                    resp = requests.post(f"{base_url}/embeddings",
                                         headers=headers, json=data, timeout=10)
            except requests.exceptions.RequestException as e:
                console.print(f"[red]❌ 连接失败: {e}[/red]")
                return

            progress.update(task, description="解析响应中...")
            time.sleep(0.5)
            progress.advance(task)

            # 5. 结果分析
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    # 根据类型解析向量维度
                    if embedding_type == 'tei':
                        # TEI可能直接返回list，或者返回{"data": [{"embedding": [...]}]}
                        if isinstance(result, list):
                            embedding_dim = len(result[0])
                        else:
                            embedding_dim = len(result["data"][0]["embedding"])
                    else:
                        # OpenAI格式
                        embedding_dim = len(result["data"][0]["embedding"])

                    progress.update(task, description="✅ 测试成功")
                    progress.advance(task)
                    console.print(f"[green]✅ Embedding 连接正常[/green]")
                    console.print(f"[bold]向量维度：[/bold] {embedding_dim}")
                    console.print(f"[bold]配置维度：[/bold] {embedding_config.get('vector_dim', '未配置')}")

                    # 检查维度是否匹配
                    if embedding_config.get('vector_dim') and embedding_dim != embedding_config['vector_dim']:
                        console.print(f"[yellow]⚠️ 警告: 实际向量维度({embedding_dim})与配置维度({embedding_config['vector_dim']})不匹配![/yellow]")
                except Exception as e:
                    console.print(f"[yellow]⚠️ 响应解析失败: {e}[/yellow]")
                    console.print(f"[yellow]响应内容: {resp.text[:200]}[/yellow]")
            else:
                console.print(f"[red]❌ 请求失败，状态码: {resp.status_code}[/red]")
                console.print(resp.text)

    elif name == "milvus":
        milvus_config = get_milvus_config()
        console.print("[bold cyan]开始测试 Milvus 连通性...[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("初始化配置...", total=5)

            # 1. 初始化
            time.sleep(0.5)
            progress.advance(task)

            # 2. 导入 pymilvus
            progress.update(task, description="导入 Milvus 客户端...")
            try:
                from pymilvus import connections, utility
            except ImportError:
                console.print("[red]❌ pymilvus 未安装，请运行: pip install pymilvus[/red]")
                return
            time.sleep(0.5)
            progress.advance(task)

            # 3. 建立连接
            progress.update(task, description="连接到 Milvus 服务...")
            time.sleep(0.5)
            progress.advance(task)

            # 4. 尝试连接
            try:
                # 构建连接参数
                connect_params = {
                    "alias": "test_connection",
                    "host": milvus_config["host"],
                    "port": milvus_config["port"],
                    "timeout": 10
                }

                # 只在有用户名和密码时添加认证信息
                user = milvus_config.get("user", "")
                password = milvus_config.get("password", "")
                if user and password:
                    connect_params["user"] = user
                    connect_params["password"] = password

                connections.connect(**connect_params)

                progress.update(task, description="验证连接状态...")
                time.sleep(0.5)
                progress.advance(task)

                # 5. 测试连接 - 使用新版本的 API
                try:
                    # 尝试获取服务器版本作为连接测试
                    server_version = utility.get_server_version(using="test_connection")
                    progress.update(task, description="✅ 测试成功")
                    progress.advance(task)
                    console.print(f"[green]✅ Milvus 连接正常[/green]")
                    console.print(f"[bold]服务器版本：[/bold] {server_version}")
                except Exception as version_error:
                    # 如果获取版本失败，尝试列出集合作为备用测试
                    try:
                        from pymilvus import list_collections
                        collections = list_collections(using="test_connection")
                        progress.update(task, description="✅ 测试成功")
                        progress.advance(task)
                        console.print(f"[green]✅ Milvus 连接正常[/green]")
                        console.print(f"[bold]集合数量：[/bold] {len(collections)}")
                    except:
                        console.print(f"[red]❌ 连接建立但无法验证: {version_error}[/red]")

                # 清理连接
                connections.disconnect("test_connection")

            except Exception as e:
                console.print(f"[red]❌ 连接失败: {e}[/red]")
                return

    elif name == "postgresql":
        pg_config = get_postgresql_config()
        console.print("[bold cyan]开始测试 PostgreSQL 连通性...[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("初始化配置...", total=5)

            # 1. 初始化
            time.sleep(0.5)
            progress.advance(task)

            # 2. 导入 psycopg2
            progress.update(task, description="导入 PostgreSQL 客户端...")
            try:
                import psycopg2
            except ImportError:
                console.print("[red]❌ psycopg2 未安装，请运行: pip install psycopg2-binary[/red]")
                return
            time.sleep(0.5)
            progress.advance(task)

            # 3. 建立连接
            progress.update(task, description="连接到 PostgreSQL 服务...")
            time.sleep(0.5)
            progress.advance(task)

            # 4. 尝试连接
            try:
                connection = psycopg2.connect(
                    host=pg_config["host"],
                    port=pg_config["port"],
                    user=pg_config["user"],
                    password=pg_config["password"],
                    database=pg_config["database"],
                    connect_timeout=10
                )

                progress.update(task, description="验证连接状态...")
                time.sleep(0.5)
                progress.advance(task)

                # 5. 测试连接
                with connection.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()[0]
                    progress.update(task, description="✅ 测试成功")
                    progress.advance(task)
                    console.print(f"[green]✅ PostgreSQL 连接正常[/green]")
                    console.print(f"[bold]服务器版本：[/bold] {version}")

                # 关闭连接
                connection.close()

            except Exception as e:
                console.print(f"[red]❌ 连接失败: {e}[/red]")
                return
        


