# 使用 Python 官方镜像
FROM python:3.9-slim-bookworm

# 设置工作目录
WORKDIR /app

# 更换为华为云镜像源
RUN sed -i 's/deb.debian.org/mirrors.huaweicloud.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.huaweicloud.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 设置 pip 使用清华镜像源
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# 安装 uv
RUN pip install --no-cache-dir uv

# 设置 uv 环境变量使用国内镜像
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1

# 复制项目依赖文件
COPY pyproject.toml uv.lock ./

# 使用 uv sync 安装依赖 (创建虚拟环境并严格遵循 lock 文件)
# 使用 BuildKit 缓存挂载，缓存下载的包
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 暴露端口
EXPOSE 5014

# 直接使用虚拟环境中的 Python 运行应用（无需 uv run，完全离线）
CMD [".venv/bin/python", "app.py"]