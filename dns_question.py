import struct

from bitarray import bitarray

from dns_name import DnsName


class DnsQuestion:
    def __init__(self, name: DnsName, q_type, q_class):
        self.name = name
        self.q_type = q_type
        self.q_class = q_class

    def get_bits(self) -> bitarray:
        result = bitarray(endian='big')
        result += self.name.get_bits()
        result.frombytes(struct.pack(">H", self.q_type))
        result.frombytes(struct.pack(">H", self.q_class))
        return result



