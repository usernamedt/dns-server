from queue import Queue

from server_config import ServerConfig
from thread_worker import Worker


class ThreadPool:
    __config = ServerConfig()

    def __init__(self):
        """
        Inits a pool of worker threads which serves the clients requests
        """
        self.tasks = Queue(self.__config.threads_count)
        self.workers = []
        for i in range(self.__config.threads_count):
            self.workers.append(Worker(self.tasks, f"worker {i} "))

    def add_task(self, func, *args, **kwargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kwargs))

    def terminate_all_workers(self):
        """Terminate all workers"""
        for pill in [None for i in range(len(self.workers))]:
            self.tasks.put(pill)
