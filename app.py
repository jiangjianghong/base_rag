from flask import Flask
from flask_cors import CORS
from api import main_bp, base_bp, init_rag_engine
from QAVectorManager.QAVectorManager import qa_vector_bp
from config.config import print_all_config, test_config
from loguru import logger

# 可选：如果需要使用案件向量管理，取消下面的注释
# from examples.HistoricalConditionCases.HistoricalConditionCases import case_vector_bp

# 添加日志文件输出（保留7天，每天轮转）
logger.add("logs/app_{time:YYYY-MM-DD}.log", rotation="00:00", retention="7 days", encoding="utf-8")

def create_app():
    app = Flask(__name__)

    # 配置CORS，允许所有来源访问
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    print_all_config()
    test_config("llm")
    test_config("embedding")
    test_config("milvus")
    test_config("postgresql")

    # 初始化RAG引擎
    with app.app_context():
        init_rag_engine()

    # 注册蓝图
    app.register_blueprint(base_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(qa_vector_bp)

    # 可选：注册案件向量管理蓝图（需要先取消导入注释）
    # app.register_blueprint(case_vector_bp)

    return app


if __name__ == "__main__":
    import logging

    # 创建一个过滤器类，过滤健康检查日志
    class HealthCheckFilter(logging.Filter):
        def filter(self, record):
            # 过滤掉健康检查的日志
            return '/main/health' not in record.getMessage()

    # 为 werkzeug 的日志添加过滤器
    log = logging.getLogger('werkzeug')
    log.addFilter(HealthCheckFilter())

    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5014)
