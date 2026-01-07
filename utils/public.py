import threading


class SingleTon(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # 第一次检查：如果实例已存在，直接返回，避开锁开销
        if cls not in cls._instances:
            with cls._lock:
                # 第二次检查：防止多线程并发进入
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def get_instance(cls):
        if cls not in cls._instances:
            raise RuntimeError(
                f"类 {cls.__name__} 尚未初始化！"
                f"请先在启动逻辑中调用一次 {cls.__name__}(db_tool) 进行初始化。"
            )
        return cls._instances[cls]
