"""
检索策略实现目录
将你的自定义检索策略实现文件放在这里

每个检索策略文件应该：
1. 从 retriever.registry 导入 retriever_registry
2. 使用 @retriever_registry.register("策略类型") 装饰器注册函数
3. 实现检索逻辑

示例：
    @retriever_registry.register("my_custom")
    def my_custom_retriever(query: str, robot: str, strategy_config: dict) -> str:
        # 你的检索逻辑
        return "检索结果"
"""
