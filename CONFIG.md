# 配置说明

## 🚀 快速开始

### 1. 复制配置文件

首次使用时，需要从示例配置创建你的配置文件：

```bash
cp config.example.yaml config.yaml
```

### 2. 修改配置

编辑 `config.yaml`，填入你的实际配置信息：

```bash
vim config.yaml
# 或使用其他编辑器
```

## 📝 配置项说明

### LLM 配置

```yaml
llm:
  api_key: "your-api-key-here"  # ⚠️ 必填：你的 LLM API Key
  base_url: "https://api.openai.com/v1"  # OpenAI 兼容的 API 地址
  model: "gpt-3.5-turbo"  # 模型名称
  temperature: 0.5  # 温度参数（0-1）
  max_tokens: 8000  # 最大生成 token 数
```

**支持的 API 提供商：**
- OpenAI
- Azure OpenAI
- 通义千问（DashScope）
- 文心一言
- 其他 OpenAI 兼容的 API

### Embedding 配置

```yaml
embedding:
  api_key: "your-api-key-here"  # API Key（TEI 类型可为空）
  base_url: "http://localhost:8080"  # Embedding 服务地址
  model: "text-embedding-ada-002"  # 模型名称
  type: "openai"  # ⚠️ 重要：可选值 "openai" 或 "tei"
  vector_dim: 1536  # 向量维度（必须与实际模型匹配）
```

**Embedding 类型说明：**

#### OpenAI 类型（`type: "openai"`）

适用于：
- OpenAI Embeddings API
- Azure OpenAI Embeddings
- 通义千问 Embeddings（DashScope）
- 其他 OpenAI 兼容的 Embedding API

请求格式：
```json
POST {base_url}/embeddings
{
  "model": "text-embedding-ada-002",
  "input": "要编码的文本"
}
```

#### TEI 类型（`type: "tei"`）

适用于：
- Hugging Face Text Embeddings Inference (TEI)
- 自部署的 TEI 服务

请求格式：
```json
POST {base_url}/embed
{
  "inputs": ["要编码的文本"]
}
```

**注意：** TEI 类型不需要 `api_key`。

### Milvus 配置

```yaml
milvus:
  host: "localhost"  # ⚠️ 必填：Milvus 服务器地址
  port: 19530  # Milvus 端口
  user: "root"  # 用户名
  password: "your-password-here"  # ⚠️ 必填：密码
```

### PostgreSQL 配置

```yaml
postgresql:
  host: "localhost"  # ⚠️ 必填：PostgreSQL 服务器地址
  port: 5432
  user: "postgres"  # ⚠️ 必填：用户名
  password: "your-password-here"  # ⚠️ 必填：密码
  database: "base_rag"  # 数据库名称
  schema: "public"  # Schema 名称
```

**初始化数据库：**

```bash
# 运行初始化脚本
python init_postgresql.py
```

### 机器人配置

```yaml
robots:
  - name: "my_bot"  # 机器人唯一标识符
    description: "我的自定义机器人"  # 描述
    prompt_template: "my_prompt"  # 对应 prompt/templates/my_prompt.md
    retriever_strategy: "my_strategy"  # 检索策略（null 表示不使用）
    enabled: true  # 是否启用
    default_config:
      structured_output: false  # 是否返回 JSON
      streaming: false  # 是否流式输出
      use_history: true  # 是否使用历史记录
      temperature: 0.7  # 可选：覆盖全局温度
```

### 检索策略配置

```yaml
retriever_strategies:
  my_strategy:
    type: "qa_vector"  # 检索类型（对应注册的检索函数）
    description: "我的检索策略"
    collection: "my_collection"  # Milvus 集合名称
    params:
      top_k: 5  # 返回 top-k 结果
      min_score: 0.5  # 最低相似度分数
      embedding_type: "embedding_all"  # 向量字段名称
      metric_type: "COSINE"  # 相似度度量（COSINE/IP/L2）
      nprobe: 10  # 搜索参数
```

## 🔒 安全最佳实践

### 1. 不要提交 config.yaml 到 Git

`config.yaml` 已被添加到 `.gitignore`，确保不会意外提交敏感信息。

### 2. 使用环境变量（可选）

对于 CI/CD 环境，可以使用环境变量：

```bash
export OPENAI_API_KEY="your-api-key"
```

配置文件会自动优先读取环境变量 `OPENAI_API_KEY`。

### 3. 权限管理

```bash
# 设置配置文件权限（Linux/Mac）
chmod 600 config.yaml
```

## 🧪 测试配置

项目提供了配置测试工具：

```bash
# 测试 LLM 连接
python -c "from config.config import test_config; test_config('llm')"

# 测试 Embedding 连接
python -c "from config.config import test_config; test_config('embedding')"

# 测试 Milvus 连接
python -c "from config.config import test_config; test_config('milvus')"

# 测试 PostgreSQL 连接
python -c "from config.config import test_config; test_config('postgresql')"
```

## 📚 常见问题

### Q1: 如何切换 LLM 提供商？

修改 `llm.base_url` 和 `llm.model` 即可：

**OpenAI:**
```yaml
base_url: "https://api.openai.com/v1"
model: "gpt-3.5-turbo"
```

**通义千问:**
```yaml
base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
model: "qwen-turbo"
```

**Azure OpenAI:**
```yaml
base_url: "https://your-resource.openai.azure.com"
model: "gpt-35-turbo"
```

### Q2: 向量维度不匹配怎么办？

确保 `embedding.vector_dim` 与实际模型输出维度一致：

- `text-embedding-ada-002`: 1536
- `text-embedding-3-small`: 1536
- `text-embedding-3-large`: 3072
- TEI (bge-large-zh-v1.5): 1024

### Q3: 如何添加新的机器人？

1. 在 `prompt/templates/` 创建 Prompt 文件
2. 在 `config.yaml` 的 `robots` 中添加配置
3. 无需修改代码，重启服务即可

### Q4: 检索策略如何自定义？

1. 在 `retriever/strategies/` 创建新的检索函数
2. 使用 `@retriever_registry.register("type_name")` 注册
3. 在 `retriever_strategies` 中配置参数

## 🔄 配置更新

修改配置后需要重启服务：

```bash
# 重启 Flask 应用
python app.py
```

---

**需要帮助？** 查看 [README.md](../README.md) 或提交 Issue。
