import struct

from bitarray import bitarray

from dns_header import DnsHeader
import io

from dns_name import DnsName
from dns_question import DnsQuestion
from dns_record import DnsRecord


class DnsMessage:
    def __init__(self, msg_bytes):
        self._orig_bytes = msg_bytes
        self.header = DnsHeader(self._orig_bytes[:12])
        self._bytestream = io.BytesIO(self._orig_bytes[12:])
        self.questions = [self._parse_question() for _ in range(self.header.total_questions)]
        self.ans_records = [self._parse_record() for _ in range(self.header.total_answer_rrs)]
        self.auth_records = [self._parse_record() for _ in range(self.header.total_authority_rrs)]
        self.add_records = [self._parse_record() for _ in range(self.header.total_additional_rrs)]

    def _parse_question(self):
        name = DnsName(self._bytestream, self._orig_bytes)
        q_type = int.from_bytes(self._bytestream.read(2), 'big')
        q_class = int.from_bytes(self._bytestream.read(2), 'big')
        return DnsQuestion(name=name, q_type=q_type, q_class=q_class)

    def _parse_record(self) -> DnsRecord:
        name = DnsName(self._bytestream, self._orig_bytes)
        ans_type = int.from_bytes(self._bytestream.read(2), 'big')
        ans_class = int.from_bytes(self._bytestream.read(2), 'big')
        ttl = int.from_bytes(self._bytestream.read(4), 'big')
        rec_len = int.from_bytes(self._bytestream.read(2), 'big')
        rec_data = self._parse_address(rec_len, ans_type)
        return DnsRecord(name=name, ans_type=ans_type, ans_class=ans_class,
                         ttl=ttl, rec_len=rec_len, rec_data=rec_data)

    def _parse_address(self, length, a_type):
        if a_type == 1:
            name = '.'.join(['{}'.format(self._bytestream.read(1)[0]) for _ in range(length)])
            return DnsName(name=name)
        elif a_type == 2:
            return DnsName(self._bytestream, self._orig_bytes)
        else:
            return DnsName(name='')

    def get_bits(self):
        result = bitarray(endian='big')
        result += self.header.header_bits
        for question in self.questions:
            result += question.get_bits()
        for answer in self.ans_records:
            result += answer.get_bits()
        return result

