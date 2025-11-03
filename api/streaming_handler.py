"""
流式处理模块
处理流式和非流式响应的统一接口
"""
import json
from typing import Generator, Dict, Any
from loguru import logger


class StreamingHandler:
    """处理流式响应的辅助类"""

    @staticmethod
    def format_sse_event(event_type: str, data: Dict[str, Any]) -> str:
        """
        格式化 SSE 事件

        Args:
            event_type: 事件类型 (streaming_start, streaming_chunk, streaming_end, streaming_error)
            data: 事件数据

        Returns:
            格式化的 SSE 字符串
        """
        event_data = json.dumps({
            "event": event_type,
            "data": data
        }, ensure_ascii=False)

        return f"data: {event_data}\n\n"

    @staticmethod
    def stream_generator(
        stream: Generator,
        question_id: str,
        robot: str = "default"
    ) -> Generator[str, None, None]:
        """
        将 LangChain 流转换为 SSE 格式的生成器

        Args:
            stream: LangChain 的流式生成器
            question_id: 问题ID
            robot: 机器人类型

        Yields:
            SSE 格式的事件字符串
        """
        try:
            # 发送开始事件
            yield StreamingHandler.format_sse_event(
                "streaming_start",
                {
                    "question_id": question_id,
                    "robot": robot
                }
            )

            # 发送内容块
            for chunk in stream:
                if chunk:  # 过滤空块
                    yield StreamingHandler.format_sse_event(
                        "streaming_chunk",
                        {
                            "content": chunk,
                            "question_id": question_id,
                            "robot": robot
                        }
                    )

            # 发送结束事件
            yield StreamingHandler.format_sse_event(
                "streaming_end",
                {
                    "complete": True,
                    "question_id": question_id,
                    "robot": robot
                }
            )

        except Exception as e:
            logger.error(f"流式处理错误: {e}")
            # 发送错误事件
            yield StreamingHandler.format_sse_event(
                "streaming_error",
                {
                    "error": str(e),
                    "question_id": question_id,
                    "robot": robot
                }
            )

    @staticmethod
    def non_streaming_generator(
        content: str,
        question_id: str,
        robot: str = "default"
    ) -> Generator[str, None, None]:
        """
        将非流式响应转换为 SSE 格式（用于统一接口）

        Args:
            content: 完整的响应内容
            question_id: 问题ID
            robot: 机器人类型

        Yields:
            SSE 格式的事件字符串
        """
        # 发送开始事件
        yield StreamingHandler.format_sse_event(
            "streaming_start",
            {
                "question_id": question_id,
                "robot": robot
            }
        )

        # 发送完整内容作为一个块
        yield StreamingHandler.format_sse_event(
            "streaming_chunk",
            {
                "content": content,
                "question_id": question_id,
                "robot": robot
            }
        )

        # 发送结束事件
        yield StreamingHandler.format_sse_event(
            "streaming_end",
            {
                "complete": True,
                "question_id": question_id,
                "robot": robot
            }
        )