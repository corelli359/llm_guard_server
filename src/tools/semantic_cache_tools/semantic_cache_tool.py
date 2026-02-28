from llm_guard_server.utils.execute_utils import Promise


class SemanticCacheTool:
    def __init__(self) -> None:
        self.promise = Promise()
