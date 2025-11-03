"""
主API蓝图 - 使用统一的RAGEngine
"""
from flask import Blueprint, request, jsonify, Response, stream_with_context
from core.rag_engine import get_rag_engine
from .streaming_handler import StreamingHandler
from .json_parser import parse_json_output
from config.config import get_robot_config
from loguru import logger
import sys
from typing import Generator

# 添加简略日志处理器
logger.remove()
brief_logger_id = logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <green>{message}</green>",
    level="INFO",
    filter=lambda record: record["extra"].get("brief", False),
    colorize=True
)


def brief(msg):
    """简略日志输出"""
    logger.bind(brief=True).info(msg)


# 创建蓝图
main_bp = Blueprint('main', __name__, url_prefix='/main')

# 全局RAG引擎实例
rag_engine = None


def init_rag_engine():
    """初始化RAG引擎（在应用启动时调用）"""
    global rag_engine
    rag_engine = get_rag_engine()
    logger.info("RAG引擎已初始化")


@main_bp.route('/chat', methods=['POST'])
def chat():
    """
    处理聊天请求（支持流式和非流式响应）

    请求体:
    {
        "question": "用户的问题",
        "robot": "机器人类型（可选，默认 default）",
        "session_id": "会话ID（当 use_history=true 时必填）",
        "streaming": true/false（可选，默认使用机器人配置的默认值）,
        "use_history": true/false（可选，默认使用机器人配置的默认值）,
        "structured_output": true/false（可选，默认使用机器人配置的默认值）,
        "temperature": 0-2之间的数字（可选，未传入时使用机器人配置或全局配置）
    }

    非流式返回:
    {
        "success": true,
        "data": {
            "answer": "AI的回答",
            "session_id": "会话ID（仅当 use_history=true 时返回）",
            "robot": "使用的机器人类型"
        }
    }

    流式返回:
    Server-Sent Events 格式，事件类型包括：
    - streaming_start: 流式开始
    - streaming_chunk: 内容块
    - streaming_end: 流式结束
    - streaming_error: 错误
    """
    try:
        data = request.get_json()
        brief(f"收到请求数据: {data}")

        if not data:
            logger.error("请求体为空")
            return jsonify({
                "success": False,
                "error": "请求体不能为空"
            }), 400

        question = data.get('question')
        robot = data.get('robot', 'default')
        session_id = data.get('session_id')

        # 读取机器人配置，获取默认值
        try:
            robot_config = get_robot_config(robot)
            default_config = robot_config.get('default_config', {})
        except ValueError as e:
            logger.error(f"获取机器人配置失败: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "error_type": "invalid_robot"
            }), 400

        # 构建运行时配置（API参数优先级高于默认配置）
        runtime_config = {}
        config_keys = ['streaming', 'use_history', 'structured_output', 'temperature', 'max_tokens']
        for key in config_keys:
            if key in data:
                runtime_config[key] = data[key]

        # 获取最终配置值（用于验证）
        streaming = data.get('streaming', default_config.get('streaming', False))
        use_history = data.get('use_history', default_config.get('use_history', True))
        structured_output = data.get('structured_output', default_config.get('structured_output', False))
        temperature = data.get('temperature', default_config.get('temperature'))

        if not question:
            logger.error("question 参数为空")
            return jsonify({
                "success": False,
                "error": "question 参数不能为空"
            }), 400

        # 验证 temperature 参数
        if temperature is not None:
            if not isinstance(temperature, (int, float)):
                logger.error(f"temperature 参数类型错误: {type(temperature)}")
                return jsonify({
                    "success": False,
                    "error": "temperature 参数必须是数字类型"
                }), 400
            if not (0 <= temperature <= 2):
                logger.error(f"temperature 参数超出范围: {temperature}")
                return jsonify({
                    "success": False,
                    "error": "temperature 参数必须在 0-2 之间"
                }), 400

        # 当 use_history=True 时，session_id 必填
        if use_history and not session_id:
            logger.error("use_history=True 时 session_id 参数为空")
            return jsonify({
                "success": False,
                "error": "使用历史记录时，session_id 参数不能为空"
            }), 400

        # 调用 RAG 引擎
        try:
            if streaming:
                # 流式处理
                stream = rag_engine.chat(
                    question=question,
                    robot=robot,
                    session_id=session_id,
                    **runtime_config
                )

                def generate() -> Generator[str, None, None]:
                    """生成 SSE 格式的响应"""
                    try:
                        for event in StreamingHandler.stream_generator(stream, session_id, robot):
                            yield event
                    except Exception as e:
                        logger.error(f"流式生成错误: {e}")
                        yield StreamingHandler.format_sse_event(
                            "streaming_error",
                            {
                                "error": str(e),
                                "session_id": session_id if use_history else None,
                                "robot": robot
                            }
                        )

                return Response(
                    stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no',
                        'Connection': 'keep-alive'
                    }
                )
            else:
                # 非流式处理
                answer = rag_engine.chat(
                    question=question,
                    robot=robot,
                    session_id=session_id,
                    **runtime_config
                )

                # 如果启用了结构化输出，解析 JSON
                if structured_output:
                    success, json_obj, error = parse_json_output(answer)

                    if success:
                        response_data = {
                            "robot": robot,
                            **json_obj
                        }
                        if use_history:
                            response_data["session_id"] = session_id

                        return jsonify({
                            "success": True,
                            "data": response_data
                        })
                    else:
                        return jsonify({
                            "success": False,
                            "error": f"JSON 解析失败: {error}",
                            "raw_output": answer
                        }), 500
                else:
                    # 未启用结构化输出，返回普通答案
                    response_data = {
                        "answer": answer,
                        "robot": robot
                    }
                    if use_history:
                        response_data["session_id"] = session_id

                    return jsonify({
                        "success": True,
                        "data": response_data
                    })

        except ValueError as e:
            logger.error(f"参数错误: {e}")
            if streaming:
                def error_generator() -> Generator[str, None, None]:
                    yield StreamingHandler.format_sse_event(
                        "streaming_error",
                        {
                            "error": str(e),
                            "error_type": "invalid_parameter",
                            "session_id": session_id if use_history else None,
                            "robot": robot
                        }
                    )
                return Response(
                    stream_with_context(error_generator()),
                    mimetype='text/event-stream',
                    status=400
                )
            else:
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "error_type": "invalid_parameter"
                }), 400

    except ValueError as e:
        logger.error(f"参数错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except Exception as e:
        logger.error(f"处理失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@main_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """
    获取指定会话的历史记录

    返回:
    {
        "success": true,
        "data": {
            "session_id": "会话ID",
            "history": [
                {"role": "human", "content": "用户消息"},
                {"role": "ai", "content": "AI消息"}
            ]
        }
    }
    """
    try:
        history = rag_engine.get_history(session_id)

        return jsonify({
            "success": True,
            "data": {
                "session_id": session_id,
                "history": history
            }
        })

    except Exception as e:
        logger.error(f"获取历史失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@main_bp.route('/history/<session_id>', methods=['DELETE'])
def clear_history(session_id):
    """
    清除指定会话的历史记录

    返回:
    {
        "success": true,
        "message": "历史记录已清除"
    }
    """
    try:
        rag_engine.clear_history(session_id)

        return jsonify({
            "success": True,
            "message": f"会话 {session_id} 的历史记录已清除"
        })

    except Exception as e:
        logger.error(f"清除历史失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@main_bp.route('/history', methods=['DELETE'])
def clear_all_history():
    """
    清除所有会话的历史记录

    返回:
    {
        "success": true,
        "message": "所有历史记录已清除"
    }
    """
    try:
        count = rag_engine.clear_all_history()

        return jsonify({
            "success": True,
            "message": f"已清除 {count} 个会话的历史记录"
        })

    except Exception as e:
        logger.error(f"清除所有历史失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@main_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """
    获取会话统计信息

    返回:
    {
        "success": true,
        "data": {
            "total_sessions": 10,
            "session_ids": ["session_001", "session_002", ...]
        }
    }
    """
    try:
        info = rag_engine.get_session_info()

        return jsonify({
            "success": True,
            "data": info
        })

    except Exception as e:
        logger.error(f"获取会话信息失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@main_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "success": True,
        "message": "RAG service is running",
        "engine_initialized": rag_engine is not None
    })
