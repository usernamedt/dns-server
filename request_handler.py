import socket
from typing import List

from cache_storage import CacheStorage
from dns_message import DnsMessage
from dns_name import DnsName
from dns_record import DnsRecord
from server_config import ServerConfig


class RequestHandler:
    def __init__(self, cache_storage: CacheStorage):
        self.__config = ServerConfig()
        self.__cache = cache_storage

    def handle_query(self, query_bytes):
        query_msg = DnsMessage(query_bytes)
        question = query_msg.questions[0]
        answers = self.__cache.get_answers(question.name.val, question.q_type)

        if not answers:
            frw_response = self.fetch_from_forwarder(query_bytes)
            if not frw_response:
                response = self.make_response(query_msg, [])
            else:
                response = frw_response
                self.__cache.add_entry(DnsMessage(frw_response))
        else:
            response = self.make_response(query_msg, answers)
        return response

    @staticmethod
    def make_response(query_msg: DnsMessage, answers: List[DnsRecord]):
        query_msg.header.total_answer_rrs = len(answers)
        query_msg.header.total_additional_rrs = 0
        query_msg.header.total_authority_rrs = 0
        query_msg.ans_records = answers
        return query_msg.get_bits()

    def fetch_from_forwarder(self, query_bytes):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.__config.forwarder_timeout)
        try:
            sock.bind(('', 0))
            sock.sendto(query_bytes, (self.__config.forwarder_host, self.__config.forwarder_port))
            return sock.recvfrom(self.__config.recv_buff_size)[0]
        except socket.timeout:
            return None
        finally:
            sock.close()
