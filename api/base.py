"""
基础API蓝图 - 提供首页和基础路由
"""
from flask import Blueprint, send_file
from loguru import logger
import os

# 创建基础蓝图(没有 url_prefix,直接在根路径)
base_bp = Blueprint('base', __name__)


@base_bp.route('/')
def index():
    """
    首页路由,返回聊天界面 HTML 文件

    返回:
    - 成功: 返回 chat-frontend.html 文件
    - 失败: 返回 JSON 格式的欢迎信息和可用接口列表
    """
    # 获取HTML文件的绝对路径
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chat-frontend.html')

    # 检查文件是否存在
    if not os.path.exists(html_path):
        logger.warning(f"聊天界面文件不存在: {html_path}")
        return {
            "message": "Welcome to Base RAG Framework",
            "error": "Chat interface not found",
            "endpoints": {
                "chat": "/main/chat",
                "history": "/main/history/<session_id>",
                "sessions": "/main/sessions",
                "health": "/main/health"
            }
        }

    # 返回HTML文件
    logger.info("返回聊天界面 HTML")
    return send_file(html_path, mimetype='text/html')
