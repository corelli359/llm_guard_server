from models.request_models import SensitiveContext
from utils.execute_utils import Promise, async_perf_count
from mock_api import mock_guard


class GuardTool:

    def __init__(self) -> None:
        self.promise: Promise = Promise()

    def flow(self):
        self.promise.then(mock_guard)

    @async_perf_count
    async def execute(self, ctx: SensitiveContext):
        return await self.promise.execute(ctx)
