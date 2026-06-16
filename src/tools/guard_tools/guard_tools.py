from models.request_models import SensitiveContext
from utils.execute_utils import Promise, async_perf_count
from mock_api import mock_guard
from .safe_guard_tool import SafeGuardToolService

service_tool = SafeGuardToolService()


class GuardTool:

    def __init__(self) -> None:
        self.promise: Promise = Promise()

    def flow(self):
        self.promise.then(service_tool.execute)
        # self.promise.then(mock_guard) # 提供给性能测试

    @async_perf_count
    async def execute(self, ctx: SensitiveContext):
        return await self.promise.execute(ctx)
