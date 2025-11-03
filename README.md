# Base RAG 项目模板

一个通用的 RAG (Retrieval-Augmented Generation) 基础模板项目，支持快速定制化开发。

## ✨ 特性

- **🎯 动态配置**: 通过配置文件定义机器人和检索策略，无需修改代码
- **📝 提示词外部化**: 提示词模板存储在独立文件中，便于管理和更新
- **🔌 可插拔检索**: 检索策略通过配置灵活切换
- **🔄 统一向量管理**: BaseVectorManager 基类消除重复代码
- **🌍 环境变量支持**: 敏感信息通过 .env 文件管理
- **📦 开箱即用**: 提供完整的示例配置和文档

## 📁 项目结构

```
base_rag/
├── app.py                      # Flask 应用入口
├── config.yaml                 # 核心配置文件
├── .env.example                # 环境变量示例
├── requirements.txt            # Python 依赖
├── config/                     # 配置管理模块
│   └── config.py              # 配置读取和验证
├── main/                       # RAG 核心模块
│   ├── main.py                # RAGChatService 主类
│   ├── streaming_handler.py   # 流式输出处理
│   └── json_parser.py         # JSON 解析器
├── prompt/                     # 提示词管理
│   ├── prompt_loader.py       # 动态提示词加载器
│   └── templates/             # 提示词模板目录
│       ├── default.txt
│       ├── ecommerce.txt
│       └── ...
├── retriever/                  # 检索模块
│   └── retriever.py           # 检索策略实现
├── vector_manager/             # 向量管理器
│   └── base_vector_manager.py # 向量管理基类
├── QAVectorManager/            # 问答向量库（核心示例）
│   └── QAVectorManager.py
├── bluepiint/                  # Flask 蓝图
│   ├── base_blueprint.py
│   └── main_blueprint.py
├── docs/                       # 文档目录
│   ├── 快速开始.md
│   ├── 自定义机器人.md
│   └── API文档.md
└── examples/                   # 可选示例代码
    ├── README.md
    └── HistoricalConditionCases/  # 案件管理示例
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd base_rag
```

### 2. 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 3. 配置环境

#### 方式一：使用环境变量（推荐）

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入实际配置
vim .env
```

#### 方式二：直接修改 config.yaml

```bash
vim config.yaml
```

### 4. 运行项目

```bash
# 使用 uv
uv run python app.py

# 或直接运行
python app.py
```

访问 `http://localhost:5014` 查看服务状态。

## 🎨 快速定制

### 添加新的机器人

1. **创建提示词模板**

在 `prompt/templates/` 目录下创建新文件，如 `medical.txt`:

```
你是一个医疗咨询助手，帮助用户解答健康相关问题...
```

2. **在 config.yaml 中注册机器人**

```yaml
robots:
  - name: "medical"
    description: "医疗咨询助手"
    prompt_template: "medical"
    retriever_strategy: "medical_kb"  # 可选
    enabled: true
```

3. **（可选）添加检索策略**

如果需要向量检索，在 `config.yaml` 中添加：

```yaml
retriever_strategies:
  medical_kb:
    type: "qa_vector"
    description: "医疗知识库检索"
    collection: "medical_qa_vectors"
    params:
      top_k: 5
      min_score: 0.6
```

完成！无需修改任何代码。

### 添加新的向量集合

1. **继承 BaseVectorManager**

```python
from vector_manager.base_vector_manager import BaseVectorManager

class MedicalVectorManager(BaseVectorManager):
    def __init__(self):
        super().__init__("medical_vectors")

    def get_collection_schema(self):
        # 定义你的 Schema
        pass

    def get_index_fields(self):
        # 定义索引字段
        pass

    def prepare_entity_data(self, data):
        # 准备数据
        pass
```

2. **注册 Flask 蓝图**（可选）

参考 `QAVectorManager.py` 的实现。

## 📚 文档

- [快速开始指南](./docs/快速开始.md)
- [自定义机器人](./docs/自定义机器人.md)
- [配置说明](./docs/配置说明.md)
- [API 接口文档](./docs/API文档.md)

## 🔧 主要配置项

### LLM 配置

```yaml
llm:
  api_key: "${LLM_API_KEY}"  # 支持环境变量
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 2000
```

### 机器人配置

```yaml
robots:
  - name: "default"
    description: "默认助手"
    prompt_template: "default"
    retriever_strategy: null
    enabled: true
```

### 检索策略配置

```yaml
retriever_strategies:
  qa_robot:
    type: "qa_vector"
    collection: "qa_vectors"
    params:
      top_k: 5
      min_score: 0.5
```

## 🌟 核心特性说明

### 1. 提示词外部化

所有提示词存储在 `prompt/templates/` 目录下的 `.txt` 文件中，支持：
- 热更新（无需重启服务）
- 版本控制
- 多语言支持
- 便于非技术人员维护

### 2. 动态机器人配置

通过 `config.yaml` 定义机器人，自动验证：
- 提示词模板是否存在
- 检索策略是否配置
- 机器人是否启用

### 3. 统一向量管理

`BaseVectorManager` 提供：
- 通用的 Milvus 连接管理
- Embedding 生成（支持 OpenAI 和 TEI 格式）
- 向量搜索封装
- 数据 CRUD 操作

### 4. 灵活的检索策略

支持：
- 无检索（纯 LLM 对话）
- 向量检索
- 自定义检索策略
- 策略参数配置

## 🔒 安全建议

1. ✅ 使用 `.env` 文件存储敏感信息
2. ✅ 将 `.env` 添加到 `.gitignore`
3. ✅ 提供 `.env.example` 作为模板
4. ✅ 在生产环境中使用密钥管理服务

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t base-rag:latest .

# 运行容器
docker run -d \
  --name base-rag-app \
  -p 5014:5014 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/.env:/app/.env:ro \
  --restart=unless-stopped \
  base-rag:latest
```

## 📝 示例内容

### 核心示例

- **QAVectorManager**: 问答向量库管理（核心功能示例）

### 机器人示例

项目包含以下预配置机器人：

- **default**: 通用助手
- **ecommerce**: 电商售前客服
- **complaint**: 投诉处理客服
- **introduction**: 产品介绍销售
- **aftersales**: 售后服务客服
- **comprehensive**: 综合咨询客服

这些示例可以直接使用或作为自定义机器人的参考。

### 可选示例

`examples/` 目录包含特定业务场景的实现示例：
- **HistoricalConditionCases**: 案件向量管理系统

根据需要选择性使用，参见 [examples/README.md](./examples/README.md)。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

在提交 PR 之前，请确保：
1. 代码通过测试
2. 更新相关文档
3. 遵循项目代码风格

## 📄 许可证

[MIT License](LICENSE)

## 🙏 致谢

本项目基于以下优秀的开源项目：
- LangChain
- Flask
- Milvus
- OpenAI API

---

**现在开始定制你自己的 RAG 应用吧！** 🎉
