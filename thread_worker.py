import logging
import traceback
from queue import Queue, Empty
from threading import Thread


class Worker(Thread):
    def __init__(self, tasks, name):
        """
        Simple thread worker, blocks if there is no tasks
        :type name: str
        :type tasks: Queue
        """
        Thread.__init__(self)
        self.tasks = tasks
        self.name = name
        self.start()

    def run(self):
        """Runs a worker endless loop until he eventually dies..."""
        while True:
            try:
                next_item = self.tasks.get(block=True)
                # if item is dead pill, exit
                if next_item is None:
                    return

                (func, args, kwargs) = next_item
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logging.error(logging.info(str(e) + ' // ' + traceback.format_exc()))
                self.tasks.task_done()
            except Empty as e:
                pass
