"""
问答库向量管理系统API接口请求示例
包含完整的请求和响应示例
"""

import requests
import json

# ============================================================================
# 1. 新增/修改接口示例
# ============================================================================

# 接口地址
UPSERT_URL = "http://172.29.50.10:5056/qa_vector/upsert"


# ============================================================================
# 示例 1.1: 批量新增问答
# ============================================================================
def example_batch_insert():
    """批量新增多个问答"""
    payload = {
        "qas": [
            {
                "qa_id": "qa_001",
                "question": "如何申请退货？",
                "answer": "您可以在订单详情页面点击\"申请退货\"按钮，填写退货原因后提交申请。我们会在24小时内审核您的退货申请。",
                "robot_type": "ecommerce"
            },
            {
                "qa_id": "qa_002",
                "question": "退货需要多长时间才能收到退款？",
                "answer": "退货商品到达我们的仓库后，我们会在3-5个工作日内完成验收，验收通过后会立即退款到您的原支付账户，到账时间根据不同支付方式一般需要1-3个工作日。",
                "robot_type": "aftersales"
            },
            {
                "qa_id": "qa_003",
                "question": "如何投诉商家？",
                "answer": "如果您对商家的服务不满意，可以通过以下方式投诉：1. 在订单页面点击\"投诉\"按钮；2. 拨打客服热线400-xxx-xxxx；3. 发送邮件至complaint@example.com。我们会认真处理您的投诉。",
                "robot_type": "complaint"
            },
            {
                "qa_id": "qa_004",
                "question": "你们公司成立多久了？",
                "answer": "我们公司成立于2010年，至今已有14年的历史。我们是国内领先的电商平台，拥有超过5000万注册用户。",
                "robot_type": "introduction"
            },
            {
                "qa_id": "qa_005",
                "question": "平台支持哪些支付方式？",
                "answer": "我们平台支持多种支付方式，包括：1. 支付宝；2. 微信支付；3. 银联卡支付；4. 信用卡支付；5. 花呗分期。您可以根据自己的需求选择合适的支付方式。",
                "robot_type": "comprehensive"
            }
        ]
    }

    response = requests.post(UPSERT_URL, json=payload)
    print("=== 批量新增问答 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_001",
    #       "status": "add",
    #       "error_msg": null
    #     },
    #     {
    #       "qa_id": "qa_002",
    #       "status": "add",
    #       "error_msg": null
    #     },
    #     {
    #       "qa_id": "qa_003",
    #       "status": "add",
    #       "error_msg": null
    #     },
    #     {
    #       "qa_id": "qa_004",
    #       "status": "add",
    #       "error_msg": null
    #     },
    #     {
    #       "qa_id": "qa_005",
    #       "status": "add",
    #       "error_msg": null
    #     }
    #   ]
    # }


# ============================================================================
# 示例 1.2: 更新已存在的问答
# ============================================================================
def example_update_qa():
    """更新已存在的问答（使用相同的qa_id）"""
    payload = {
        "qas": [
            {
                "qa_id": "qa_001",  # 已存在的ID
                "question": "如何申请退货？",
                "answer": "您可以在订单详情页面点击\"申请退货\"按钮，填写退货原因后提交申请。我们会在24小时内审核您的退货申请。审核通过后，请在7天内将商品寄回。温馨提示：退货商品需保持包装完整，不影响二次销售。",
                # 更新后的答案，添加了更多细节
                "robot_type": "ecommerce"
            }
        ]
    }

    response = requests.post(UPSERT_URL, json=payload)
    print("=== 更新已存在问答 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_001",
    #       "status": "update",
    #       "error_msg": null
    #     }
    #   ]
    # }


# ============================================================================
# 示例 1.3: 混合操作（新增+更新）
# ============================================================================
def example_mixed_operations():
    """同时包含新增和更新操作"""
    payload = {
        "qas": [
            {
                "qa_id": "qa_001",  # 已存在，会更新
                "question": "如何申请退货？",
                "answer": "最新退货流程：请在订单页面申请退货，填写原因并上传商品照片。",
                "robot_type": "ecommerce"
            },
            {
                "qa_id": "qa_006",  # 不存在，会新增
                "question": "如何修改收货地址？",
                "answer": "如果订单未发货，您可以在订单详情页面点击\"修改地址\"按钮进行修改。如果已发货，请联系客服处理。",
                "robot_type": "ecommerce"
            },
            {
                "qa_id": "qa_002",  # 已存在，会更新
                "question": "退货需要多长时间才能收到退款？",
                "answer": "退货商品到达仓库后，3-5个工作日内完成验收并退款，退款到账时间1-3个工作日。",
                "robot_type": "aftersales"
            }
        ]
    }

    response = requests.post(UPSERT_URL, json=payload)
    print("=== 混合操作（新增+更新）===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_001",
    #       "status": "update",
    #       "error_msg": null
    #     },
    #     {
    #       "qa_id": "qa_006",
    #       "status": "add",
    #       "error_msg": null
    #     },
    #     {
    #       "qa_id": "qa_002",
    #       "status": "update",
    #       "error_msg": null
    #     }
    #   ]
    # }


# ============================================================================
# 示例 1.4: 不带robot_type的问答
# ============================================================================
def example_without_robot_type():
    """添加不指定robot_type的问答"""
    payload = {
        "qas": [
            {
                "qa_id": "qa_007",
                "question": "客服工作时间是什么？",
                "answer": "我们的客服工作时间是每天9:00-21:00，节假日正常服务。"
                # 不指定robot_type
            }
        ]
    }

    response = requests.post(UPSERT_URL, json=payload)
    print("=== 不带robot_type的问答 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_007",
    #       "status": "add",
    #       "error_msg": null
    #     }
    #   ]
    # }


# ============================================================================
# 示例 1.5: 错误处理示例
# ============================================================================
def example_error_handling():
    """包含错误数据的请求"""
    payload = {
        "qas": [
            {
                "qa_id": "qa_008",
                "question": "正常问题",
                "answer": "正常答案",
                "robot_type": "ecommerce"
            },
            {
                "qa_id": "qa_009",
                "question": "缺少answer字段的问题"
                # 缺少 answer 字段
            },
            {
                "qa_id": "qa_010",
                # 缺少 question 字段
                "answer": "缺少question字段的答案"
            },
            {
                "qa_id": "qa_011",
                "question": "错误的robot_type",
                "answer": "测试错误的robot_type",
                "robot_type": "invalid_type"  # 无效的robot_type
            },
            {
                "qa_id": "qa_012",
                "question": "正常问题2",
                "answer": "正常答案2",
                "robot_type": "aftersales"
            }
        ]
    }

    response = requests.post(UPSERT_URL, json=payload)
    print("=== 错误处理示例 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_008",
    #       "status": "add",
    #       "error_msg": null
    #     },
    #     {
    #       "qa_id": "qa_009",
    #       "status": "error",
    #       "error_msg": "缺少必填字段: qa_id, question, answer"
    #     },
    #     {
    #       "qa_id": "qa_010",
    #       "status": "error",
    #       "error_msg": "缺少必填字段: qa_id, question, answer"
    #     },
    #     {
    #       "qa_id": "qa_011",
    #       "status": "error",
    #       "error_msg": "robot_type无效，必须是以下之一: ecommerce, complaint, introduction, aftersales, comprehensive"
    #     },
    #     {
    #       "qa_id": "qa_012",
    #       "status": "add",
    #       "error_msg": null
    #     }
    #   ]
    # }


# ============================================================================
# 2. 搜索接口示例
# ============================================================================

# 接口地址
SEARCH_URL = "http://172.29.50.10:5056/qa_vector/search"


# ============================================================================
# 示例 2.1: 基础搜索（搜索全部问答，使用默认参数）
# ============================================================================
def example_basic_search():
    """基础搜索，不限制qa_id，使用默认参数"""
    payload = {
        "query_str": "怎么退货",
        # qa_ids 不传或传空列表，表示搜索全部
        # top_k 不传，默认10条
        # min_score 不传，不过滤分数
        # robot_type 不传，搜索所有类型
        # embedding_type 不传，默认使用 embedding_question
    }

    response = requests.post(SEARCH_URL, json=payload)
    print("=== 基础搜索（搜索全部）===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_001",
    #       "question": "如何申请退货？",
    #       "answer": "您可以在订单详情页面点击"申请退货"按钮...",
    #       "score": 0.9256
    #     },
    #     {
    #       "qa_id": "qa_002",
    #       "question": "退货需要多长时间才能收到退款？",
    #       "answer": "退货商品到达我们的仓库后...",
    #       "score": 0.8134
    #     }
    #   ]
    # }


# ============================================================================
# 示例 2.2: 限制搜索范围（指定qa_ids）
# ============================================================================
def example_filtered_search_by_qa_ids():
    """只在指定的qa_id列表中搜索"""
    payload = {
        "qa_ids": ["qa_001", "qa_002", "qa_003"],
        "query_str": "投诉",
        "top_k": 5
    }

    response = requests.post(SEARCH_URL, json=payload)
    print("=== 限制搜索范围（指定qa_ids）===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_003",
    #       "question": "如何投诉商家？",
    #       "answer": "如果您对商家的服务不满意...",
    #       "score": 0.9523
    #     }
    #   ]
    # }


# ============================================================================
# 示例 2.3: 按robot_type过滤
# ============================================================================
def example_search_by_robot_type():
    """按场景类型过滤搜索结果"""
    payload = {
        "query_str": "退货",
        "robot_type": "ecommerce",  # 只搜索电商类型的问答
        "top_k": 10
    }

    response = requests.post(SEARCH_URL, json=payload)
    print("=== 按robot_type过滤 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_001",
    #       "question": "如何申请退货？",
    #       "answer": "您可以在订单详情页面点击"申请退货"按钮...",
    #       "score": 0.9256
    #     }
    #     // 只返回 robot_type 为 ecommerce 的结果
    #   ]
    # }


# ============================================================================
# 示例 2.4: 使用最低分数过滤
# ============================================================================
def example_search_with_min_score():
    """使用最低分数过滤，只返回相似度高于阈值的结果"""
    payload = {
        "query_str": "支付方式",
        "top_k": 20,
        "min_score": 0.7  # 只返回相似度 >= 0.7 的结果
    }

    response = requests.post(SEARCH_URL, json=payload)
    print("=== 使用最低分数过滤 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_005",
    #       "question": "平台支持哪些支付方式？",
    #       "answer": "我们平台支持多种支付方式...",
    #       "score": 0.8945
    #     }
    #     // 只返回 score >= 0.7 的结果
    #   ]
    # }


# ============================================================================
# 示例 2.5: 使用不同的embedding_type（搜索问题向量）
# ============================================================================
def example_search_by_question_embedding():
    """使用问题向量进行搜索（默认方式）"""
    payload = {
        "query_str": "如何退款",
        "embedding_type": "embedding_question",  # 使用问题向量
        "top_k": 5
    }

    response = requests.post(SEARCH_URL, json=payload)
    print("=== 使用问题向量搜索 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_002",
    #       "question": "退货需要多长时间才能收到退款？",
    #       "answer": "退货商品到达我们的仓库后...",
    #       "score": 0.9123
    #     }
    #   ]
    # }


# ============================================================================
# 示例 2.6: 使用不同的embedding_type（搜索答案向量）
# ============================================================================
def example_search_by_answer_embedding():
    """使用答案向量进行搜索"""
    payload = {
        "query_str": "24小时内审核",
        "embedding_type": "embedding_answer",  # 使用答案向量
        "top_k": 5
    }

    response = requests.post(SEARCH_URL, json=payload)
    print("=== 使用答案向量搜索 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_001",
    #       "question": "如何申请退货？",
    #       "answer": "您可以在订单详情页面点击"申请退货"按钮，填写退货原因后提交申请。我们会在24小时内审核您的退货申请。",
    #       "score": 0.8756
    #     }
    #   ]
    # }


# ============================================================================
# 示例 2.7: 使用不同的embedding_type（搜索问题+答案向量）
# ============================================================================
def example_search_by_all_embedding():
    """使用问题+答案混合向量进行搜索"""
    payload = {
        "query_str": "退货流程和时间",
        "embedding_type": "embedding_all",  # 使用问题+答案向量
        "top_k": 5
    }

    response = requests.post(SEARCH_URL, json=payload)
    print("=== 使用问题+答案向量搜索 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_001",
    #       "question": "如何申请退货？",
    #       "answer": "您可以在订单详情页面点击"申请退货"按钮...",
    #       "score": 0.9012
    #     },
    #     {
    #       "qa_id": "qa_002",
    #       "question": "退货需要多长时间才能收到退款？",
    #       "answer": "退货商品到达我们的仓库后...",
    #       "score": 0.8567
    #     }
    #   ]
    # }


# ============================================================================
# 示例 2.8: 完整参数搜索
# ============================================================================
def example_full_parameter_search():
    """使用所有参数进行精确搜索"""
    payload = {
        "qa_ids": ["qa_001", "qa_002", "qa_003", "qa_005", "qa_006"],
        "query_str": "退货退款流程",
        "top_k": 3,
        "min_score": 0.6,
        "robot_type": "ecommerce",
        "embedding_type": "embedding_all"
    }

    response = requests.post(SEARCH_URL, json=payload)
    print("=== 完整参数搜索 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": [
    #     {
    #       "qa_id": "qa_001",
    #       "question": "如何申请退货？",
    #       "answer": "您可以在订单详情页面点击"申请退货"按钮...",
    #       "score": 0.8567
    #     }
    #   ]
    # }


# ============================================================================
# 示例 2.9: 多场景类型对比搜索
# ============================================================================
def example_compare_robot_types():
    """对比不同场景类型的搜索结果"""
    query = "如何处理售后问题"

    print("=== 多场景类型对比搜索 ===")

    # 搜索所有类型
    payload_all = {
        "query_str": query,
        "top_k": 3
    }
    response_all = requests.post(SEARCH_URL, json=payload_all)
    print("1. 搜索所有类型:")
    print(f"响应:\n{json.dumps(response_all.json(), ensure_ascii=False, indent=2)}\n")

    # 只搜索售后类型
    payload_aftersales = {
        "query_str": query,
        "robot_type": "aftersales",
        "top_k": 3
    }
    response_aftersales = requests.post(SEARCH_URL, json=payload_aftersales)
    print("2. 只搜索售后类型:")
    print(f"响应:\n{json.dumps(response_aftersales.json(), ensure_ascii=False, indent=2)}\n")

    # 只搜索投诉类型
    payload_complaint = {
        "query_str": query,
        "robot_type": "complaint",
        "top_k": 3
    }
    response_complaint = requests.post(SEARCH_URL, json=payload_complaint)
    print("3. 只搜索投诉类型:")
    print(f"响应:\n{json.dumps(response_complaint.json(), ensure_ascii=False, indent=2)}\n")


# ============================================================================
# 示例 2.10: 空结果示例
# ============================================================================
def example_empty_results():
    """搜索没有匹配结果的情况"""
    payload = {
        "query_str": "完全不相关的查询内容xyz123",
        "min_score": 0.95  # 设置很高的阈值
    }

    response = requests.post(SEARCH_URL, json=payload)
    print("=== 空结果示例 ===")
    print(f"请求体:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 预期响应:
    # {
    #   "success": true,
    #   "results": []
    # }


# ============================================================================
# 示例 2.11: 错误参数示例
# ============================================================================
def example_invalid_parameters():
    """测试无效参数的处理"""

    print("=== 错误参数示例 ===")

    # 缺少query_str
    payload_no_query = {
        "top_k": 10
    }
    response = requests.post(SEARCH_URL, json=payload_no_query)
    print("1. 缺少query_str参数:")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")

    # 无效的embedding_type
    payload_invalid_embedding = {
        "query_str": "测试",
        "embedding_type": "invalid_embedding"
    }
    response = requests.post(SEARCH_URL, json=payload_invalid_embedding)
    print("2. 无效的embedding_type:")
    print(f"响应:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")


# ============================================================================
# 使用 curl 命令示例
# ============================================================================

CURL_EXAMPLES = """
# ============================================================================
# 使用 curl 命令调用接口
# ============================================================================

# ----------------------------------------
# 1. 初始化接口
# ----------------------------------------
curl -X POST http://172.29.50.10:5056/qa_vector/init \\
  -H "Content-Type: application/json"

# ----------------------------------------
# 2. 新增/修改接口
# ----------------------------------------

# 2.1 新增单个问答
curl -X POST http://172.29.50.10:5056/qa_vector/upsert \\
  -H "Content-Type: application/json" \\
  -d '{
    "qas": [
      {
        "qa_id": "qa_001",
        "question": "如何申请退货？",
        "answer": "您可以在订单详情页面点击申请退货按钮",
        "robot_type": "ecommerce"
      }
    ]
  }'

# 2.2 批量新增问答
curl -X POST http://172.29.50.10:5056/qa_vector/upsert \\
  -H "Content-Type: application/json" \\
  -d '{
    "qas": [
      {
        "qa_id": "qa_001",
        "question": "如何申请退货？",
        "answer": "您可以在订单详情页面点击申请退货按钮",
        "robot_type": "ecommerce"
      },
      {
        "qa_id": "qa_002",
        "question": "退货需要多长时间？",
        "answer": "退货商品到达仓库后3-5个工作日完成验收",
        "robot_type": "aftersales"
      }
    ]
  }'

# 2.3 更新已存在的问答
curl -X POST http://172.29.50.10:5056/qa_vector/upsert \\
  -H "Content-Type: application/json" \\
  -d '{
    "qas": [
      {
        "qa_id": "qa_001",
        "question": "如何申请退货？",
        "answer": "更新后的答案内容",
        "robot_type": "ecommerce"
      }
    ]
  }'

# ----------------------------------------
# 3. 搜索接口
# ----------------------------------------

# 3.1 基础搜索（最简单）
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query_str": "怎么退货"
  }'

# 3.2 限制返回条数
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query_str": "退货",
    "top_k": 5
  }'

# 3.3 按robot_type过滤
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query_str": "退货",
    "robot_type": "ecommerce",
    "top_k": 10
  }'

# 3.4 限制搜索范围（指定qa_ids）
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "qa_ids": ["qa_001", "qa_002", "qa_003"],
    "query_str": "退货",
    "top_k": 5
  }'

# 3.5 使用最低分数过滤
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query_str": "支付方式",
    "min_score": 0.7,
    "top_k": 10
  }'

# 3.6 使用问题向量搜索（默认）
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query_str": "如何退款",
    "embedding_type": "embedding_question",
    "top_k": 5
  }'

# 3.7 使用答案向量搜索
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query_str": "24小时内审核",
    "embedding_type": "embedding_answer",
    "top_k": 5
  }'

# 3.8 使用问题+答案向量搜索
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query_str": "退货流程和时间",
    "embedding_type": "embedding_all",
    "top_k": 5
  }'

# 3.9 完整参数搜索
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "qa_ids": ["qa_001", "qa_002", "qa_003", "qa_005"],
    "query_str": "退货退款流程",
    "top_k": 3,
    "min_score": 0.6,
    "robot_type": "ecommerce",
    "embedding_type": "embedding_all"
  }'

# ----------------------------------------
# 4. 实用技巧
# ----------------------------------------

# 4.1 格式化输出（使用 jq）
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{"query_str": "退货"}' | jq '.'

# 4.2 只查看成功状态
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{"query_str": "退货"}' | jq '.success'

# 4.3 只查看结果数量
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{"query_str": "退货"}' | jq '.results | length'

# 4.4 提取所有qa_id
curl -X POST http://172.29.50.10:5056/qa_vector/search \\
  -H "Content-Type: application/json" \\
  -d '{"query_str": "退货"}' | jq '.results[].qa_id'
"""

# ============================================================================
# Python requests 使用技巧
# ============================================================================

PYTHON_TIPS = """
# ============================================================================
# Python requests 使用技巧
# ============================================================================

# 1. 处理响应
response = requests.post(SEARCH_URL, json=payload)
if response.status_code == 200:
    result = response.json()
    if result['success']:
        for item in result['results']:
            print(f"QA ID: {item['qa_id']}")
            print(f"Question: {item['question']}")
            print(f"Answer: {item['answer']}")
            print(f"Score: {item['score']}")
            print("-" * 50)
else:
    print(f"请求失败: {response.status_code}")

# 2. 批量插入并检查失败项
response = requests.post(UPSERT_URL, json=payload)
result = response.json()
if result['success']:
    failed_items = [r for r in result['results'] if r['status'] == 'error']
    if failed_items:
        print(f"有 {len(failed_items)} 条数据插入失败:")
        for item in failed_items:
            print(f"  QA ID: {item['qa_id']}, 错误: {item['error_msg']}")
    else:
        print("所有数据处理成功")

# 3. 设置超时
response = requests.post(SEARCH_URL, json=payload, timeout=30)

# 4. 异常处理
try:
    response = requests.post(SEARCH_URL, json=payload, timeout=30)
    response.raise_for_status()  # 如果状态码不是2xx，抛出异常
    result = response.json()
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.RequestException as e:
    print(f"请求异常: {e}")
"""

# ============================================================================
# 主函数
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("问答库向量管理系统API接口请求示例")
    print("=" * 80 + "\n")

    # 可以取消注释运行具体示例
    # 注意：首次运行前需要确保服务已启动，并且已调用初始化接口

    # ========== 新增/修改接口示例 ==========
    print("\n" + "=" * 80)
    print("新增/修改接口示例")
    print("=" * 80 + "\n")

    example_batch_insert()
    example_update_qa()
    example_mixed_operations()
    example_without_robot_type()
    example_error_handling()

    # ========== 搜索接口示例 ==========
    print("\n" + "=" * 80)
    print("搜索接口示例")
    print("=" * 80 + "\n")

    example_basic_search()
    example_filtered_search_by_qa_ids()
    example_search_by_robot_type()
    example_search_with_min_score()
    example_search_by_question_embedding()
    example_search_by_answer_embedding()
    example_search_by_all_embedding()
    example_full_parameter_search()
    example_compare_robot_types()
    example_empty_results()
    example_invalid_parameters()

    # ========== 打印curl和Python使用技巧 ==========
    print("\n" + "=" * 80)
    print("curl 命令示例")
    print("=" * 80)
    print(CURL_EXAMPLES)

    print("\n" + "=" * 80)
    print("Python 使用技巧")
    print("=" * 80)
    print(PYTHON_TIPS)
