import os
import asyncio
from datetime import datetime, time
from sanic.log import logger
from tools.data_tool import DataInitPromise


class ScheduledTaskManager:
    """定时任务管理器"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.tasks = []

    def schedule_interval_task(self, minutes:int, task_func,task_name:str=""):
        """
        调度间隔定时任务
        :param minutes:
        :param task_func:
        :param task_name:
        :return:
        """
        task = self._create_interval_task(minutes, task_func, task_name)
        self.tasks.append(task)
        return task

    def _create_interval_task(self, minutes:int, task_func, task_name:str):
        async def interval_task_wrapper():
            while True:
                try:
                    await task_func()
                except Exception as e:
                    logger.error(f"[{datetime.now()}]定时任务[{task_name}执行失败:{e}]", exc_info=True)
                finally:
                    await asyncio.sleep(minutes*60) # 等待N分钟
        return interval_task_wrapper()

    def schedule_daily_task(self, hour: int, minute: int, task_func, task_name: str = ""):
        """
        调度每日定时任务
        :param hour: 小时(0-23)
        :param minute: 分钟(0-59)
        :param task_func: 异步任务函数
        :param task_name: 任务名称
        :return:
        """
        task = self._create_daily_task(hour, minute, task_func, task_name)
        self.tasks.append(task)
        return task

    async def _create_daily_task(self, hour: int, minute: int, task_func, task_name: str):
        """创建每日定时任务"""
        task_name = task_name or task_func.__name__
        while True:
            try:
                now = datetime.now()
                target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                # 如果今天的时间已经过了，则设置为明天
                if now.time() >= target.time():
                    from datetime import timedelta
                    target = target + timedelta(days=1)

                # 计算等待时间
                wait_seconds = (target - now).total_seconds()

                logger.info(
                    f"[ScheduledTask] Task '{task_name}' scheduled to run at"
                    f"{target.strftime('%Y-%m-%d %H:%M:%S')},"
                    f"waiting for {wait_seconds:.2f} seconds"
                )
                # 等待到指定时间
                await asyncio.sleep(wait_seconds)

                # 执行任务
                logger.info(f"[ScheduledTask] Starting task '{task_name}'")

                start_time = datetime.now()
                try:
                    if asyncio.iscoroutinefunction(task_func):
                        result = await task_func()
                    else:
                        result = task_func()

                    elapsed = (datetime.now() - start_time).total_seconds()
                    logger.info(
                        f"[ScheduledTask] Task '{task_name}' completed successfully"
                        f"in {elapsed:.2f} seconds"
                    )
                except Exception as e:
                    logger.error(
                        f"[ScheduledTask] Task '{task_name}' failed:{e}"
                    )
            except asyncio.CancelledError:
                logger.info(f"[ScheduledTask] Task '{task_name}' cancelled")
                break
            except Exception as e:
                logger.error(
                    f"[ScheduledTask] Error in task '{task_name}': {e}",
                    exc_info=True
                )
                # 等待一分钟再试？

    async def start_all_tasks(self):
        """启动所有定时任务"""
        logger.info(f"[ScheduledTask] Starting {len(self.tasks)} scheduled tasks")

        # 并发启动所有任务
        await asyncio.gather(*self.tasks, return_exceptions=True)

    def cancel_all_tasks(self):
        """取消所有定时任务"""
        for task in self.tasks:
            if isinstance(task, asyncio.Task):
                task.cancel()
        logger.info("[ScheduledTask] All tasks cancelled")


def setup_scheduled_tasks(app):
    """
    设置定时任务
    :param app:
    :return:
    """

    @app.after_server_start
    async def start_scheduler(app):
        pass
        # try:
        #     scheduler = ScheduledTaskManager()
        #     IS_PROD = os.getenv("PROD", 'false')
        #     if IS_PROD == 'true':
        #         # 生产环境每晚执行
        #         await scheduler.schedule_daily_task(
        #             hour=23,
        #             minute=50,
        #             task_func=DataInitPromise().reload_all_data,
        #             task_name="daily_data_reload"
        #         )
        #     else:
        #         # 测试环境每隔五分钟执行一次
        #         await scheduler.schedule_interval_task(
        #             minutes=5,
        #             task_func=DataInitPromise().reload_all_data,
        #             task_name='daily_interval_reload'
        #         )
        #     # 启动定时任务
        #     await scheduler.start_all_tasks()
        # except Exception as e:
        #     logger.error(f"[ScheduledTask] 定时任务启动失败:{e}", exc_info=True)

    @app.before_server_stop
    async def stop_scheduler(app):
        try:
            scheduler = ScheduledTaskManager()
            scheduler.cancel_all_tasks()
            logger.info("[ScheduledTask] Schedulter stopped")
        except Exception as e:
            logger.info(f"[ScheduledTask] Error stopping scheduler:{e}")