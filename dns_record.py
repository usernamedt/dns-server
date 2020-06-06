import struct
from time import time

from bitarray import bitarray

from dns_name import DnsName


class DnsRecord:
    def __init__(self, name: DnsName, ans_type, ans_class, ttl, rec_len, rec_data: DnsName):
        self.name = name
        self.ans_type = ans_type
        self.ans_class = ans_class
        self._ttl = int(ttl)
        self.rec_len = rec_len
        self.rec_data = rec_data
        self.recv_time = time()

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, val):
        self._ttl = int(val)

    def get_bits(self) -> bitarray:
        result = bitarray(endian='big')
        result += self.name.get_bits()
        result.frombytes(struct.pack(">H", self.ans_type))
        result.frombytes(struct.pack(">H", self.ans_class))
        result.frombytes(struct.pack(">I", self._ttl if self._ttl > 0 else 0))
        result.frombytes(struct.pack(">H", self.rec_len))
        if self.ans_type == 1:
            result += self.rec_data.get_ip_bits()
        else:
            result += self.rec_data.get_bits()
        return result
