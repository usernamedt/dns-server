import struct

from bitarray import bitarray
from bitarray.util import ba2int


class DnsHeader:
    def __init__(self, h_bytes):
        self.header_bits = bitarray(endian='big')
        self.header_bits.frombytes(h_bytes)

    def get_bytes(self):
        return self.header_bits.tobytes()

    @property
    def identification(self):
        return ba2int(self.header_bits[:16])

    @property
    def qr(self):
        return ba2int(self.header_bits[16:17])

    @property
    def op_code(self):
        return ba2int(self.header_bits[17:21])

    @property
    def aa(self):
        return int(self.header_bits[21])

    @property
    def tc(self):
        return int(self.header_bits[22])

    @property
    def rd(self):
        return int(self.header_bits[23])

    @property
    def ra(self):
        return int(self.header_bits[24])

    @property
    def z(self):
        return int(self.header_bits[25])

    @property
    def ad(self):
        return int(self.header_bits[26])

    @property
    def cd(self):
        return int(self.header_bits[27])

    @property
    def r_code(self):
        return ba2int(self.header_bits[28:32])

    @property
    def total_questions(self):
        return ba2int(self.header_bits[32:48])

    @property
    def total_answer_rrs(self):
        return ba2int(self.header_bits[48:64])

    @total_answer_rrs.setter
    def total_answer_rrs(self, val):
        bits = bitarray(endian='big')
        bits.frombytes(struct.pack(">H", val))
        self._update_bits(48, bits)

    @property
    def total_authority_rrs(self):
        return ba2int(self.header_bits[64:80])

    @total_authority_rrs.setter
    def total_authority_rrs(self, val):
        bits = bitarray(endian='big')
        bits.frombytes(struct.pack(">H", val))
        self._update_bits(64, bits)

    @property
    def total_additional_rrs(self):
        return ba2int(self.header_bits[80:])

    @total_additional_rrs.setter
    def total_additional_rrs(self, val):
        bits = bitarray(endian='big')
        bits.frombytes(struct.pack(">H", val))
        self._update_bits(80, bits)

    def _update_bits(self, idx, bits):
        self.header_bits = self.header_bits[:idx] + bits + self.header_bits[idx + len(bits):]
