import io
import struct

from bitarray import bitarray


class DnsName:
    def __init__(self, bytestream: io.BytesIO = None, src_bytes=None, name=None):
        if bytestream is not None:
            self.val = self._parse(bytestream, src_bytes)
        else:
            self.val = name

    def __str__(self):
        return self.val

    def _parse(self, bytestream, src_bytes=None):
        length = bytestream.read(1)[0]
        if length != 0:
            if length < 192:
                name = f"{bytestream.read(length).decode('ASCII')}."
                rec_name = self._parse(bytestream, src_bytes)
                return (name + rec_name).rstrip('.')
            else:
                second_part = bytestream.read(1)[0]
                offset = (length - 192) * 256 + second_part
                return self._parse(io.BytesIO(src_bytes[offset:]))
        else:
            return ''

    def get_bits(self) -> bitarray:
        result = bitarray(endian='big')
        for fragment in self.val.split('.'):
            result.frombytes(struct.pack(">B", len(fragment)))
            result.frombytes(bytes(fragment, 'ASCII'))
        result.frombytes(struct.pack(">B", 0))
        return result

    def get_ip_bits(self) -> bitarray:
        result = bitarray(endian='big')
        for fragment in self.val.split('.'):
            result.frombytes(struct.pack(">B", int(fragment)))
        return result
