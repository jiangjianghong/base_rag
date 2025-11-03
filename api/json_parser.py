"""
JSON解析工具模块
用于从LLM输出中提取和解析JSON格式的内容
"""

import json
import re
from typing import Dict, Any, Optional, Tuple
from loguru import logger


def extract_json_from_text(text: str) -> Optional[str]:
    """
    从文本中提取JSON字符串

    支持以下格式：
    1. 纯JSON: {"key": "value"}
    2. Markdown代码块: ```json\n{...}\n```
    3. 混合文本: 一些文字 {"key": "value"} 一些文字

    Args:
        text: 包含JSON的文本

    Returns:
        提取到的JSON字符串，如果未找到返回None
    """
    if not text or not isinstance(text, str):
        return None

    text = text.strip()

    # 方法1: 尝试直接解析（纯JSON）
    if text.startswith('{') or text.startswith('['):
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

    # 方法2: 提取Markdown代码块中的JSON
    # 匹配 ```json...``` 或 ```...```
    code_block_patterns = [
        r'```json\s*\n(.*?)\n```',
        r'```\s*\n(.*?)\n```',
    ]

    for pattern in code_block_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

    # 方法3: 查找第一个完整的JSON对象或数组
    # 匹配 {...} 或 [...]
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # 匹配嵌套的对象
        r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]',  # 匹配嵌套的数组
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

    return None


def parse_json_output(text: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    解析LLM输出的JSON内容

    Args:
        text: LLM的输出文本

    Returns:
        (成功标志, 解析后的JSON对象, 错误信息)
        - 成功: (True, json_dict, None)
        - 失败: (False, None, error_message)
    """
    if not text:
        return False, None, "输出内容为空"

    # 提取JSON字符串
    json_str = extract_json_from_text(text)

    if not json_str:
        return False, None, "未能从输出中提取有效的JSON格式"

    # 解析JSON
    try:
        json_obj = json.loads(json_str)
        logger.info(f"成功解析JSON输出，包含 {len(json_obj) if isinstance(json_obj, dict) else len(json_obj)} 个元素")
        return True, json_obj, None
    except json.JSONDecodeError as e:
        error_msg = f"JSON解析失败: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg


def validate_json_structure(json_obj: Dict[str, Any], required_keys: list = None) -> Tuple[bool, Optional[str]]:
    """
    验证JSON对象的结构

    Args:
        json_obj: 要验证的JSON对象
        required_keys: 必需的键列表（可选）

    Returns:
        (是否有效, 错误信息)
    """
    if not isinstance(json_obj, dict):
        return False, "JSON必须是一个对象（字典）"

    if required_keys:
        missing_keys = [key for key in required_keys if key not in json_obj]
        if missing_keys:
            return False, f"缺少必需的字段: {', '.join(missing_keys)}"

    return True, None


def format_json_response(json_obj: Any) -> str:
    """
    格式化JSON对象为美化的字符串

    Args:
        json_obj: JSON对象

    Returns:
        格式化后的JSON字符串
    """
    try:
        return json.dumps(json_obj, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"JSON格式化失败: {e}")
        return str(json_obj)


# 测试函数
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        # 纯JSON
        '{"name": "张三", "age": 30}',

        # Markdown代码块
        '''这是一些文字
```json
{
  "name": "李四",
  "age": 25
}
```
更多文字''',

        # 混合文本
        '根据您的要求，这里是结果：{"status": "success", "data": [1, 2, 3]}',

        # 嵌套JSON
        '{"user": {"name": "王五", "address": {"city": "北京"}}}',

        # 无效的JSON
        '这段文字没有JSON',

        # 不完整的JSON
        '{"name": "赵六"',
    ]

    print("=" * 60)
    print("JSON解析工具测试")
    print("=" * 60)

    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"输入: {test_text[:50]}...")

        success, json_obj, error = parse_json_output(test_text)

        if success:
            print(f"✓ 解析成功:")
            print(format_json_response(json_obj))
        else:
            print(f"✗ 解析失败: {error}")
