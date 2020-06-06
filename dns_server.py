import logging
import signal
import sys
import traceback
from pathlib import Path
from socket import socket, AF_INET, SOCK_DGRAM

from cache_storage import CacheStorage
from dns_message import DnsMessage
from server_config import ServerConfig
from thread_pool import ThreadPool
from request_handler import RequestHandler


class DnsServer:
    def __init__(self, config_name="config.json"):
        self.__config = ServerConfig(config_name)
        logging.basicConfig(filename=self.__config.log_file,
                            level=logging.DEBUG,
                            format='%(asctime)s %(message)s')
        self.thread_pool = ThreadPool()
        cache_dir = Path.cwd() / self.__config.cache_dir
        self.cache = CacheStorage(cache_dir)
        self.request_handler = RequestHandler(self.cache)

    def run(self):
        """Binds, listens, processing DNS requests on socket"""
        signal.signal(signal.SIGINT, self.__handle_exit)
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind((self.__config.server_host, self.__config.server_port))
        s.settimeout(self.__config.server_timeout)
        logging.info(f'Launched at {self.__config.server_host}:{self.__config.server_port}')
        while True:
            try:
                data, addr = s.recvfrom(self.__config.recv_buff_size)
            except SystemExit as e:
                s.close()
                break
            except Exception as e:
                logging.info(str(e))
                s.close()
                break

            self.thread_pool.add_task(self.__process_request, data, addr, s)

    def __process_request(self, data, addr, s_socket):
        response = self.request_handler.handle_query(data)
        s_socket.sendto(response, addr)

    def __handle_exit(self, signal, frame):
        logging.info("Received SIGINT, shutting down threads...")
        print("shutting down...")
        self.thread_pool.tasks.join()
        self.thread_pool.terminate_all_workers()
        logging.info("Threads stopped, updating cache")
        self.cache.cleanup()
        sys.exit(0)
