import io
import struct

_endians = {'big': '>', 'little': '<'}
_unsigned_int_formats = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}
_signed_int_formats = {1: 'b', 2: 'h', 4: 'i', 8: 'q'}
_float_formats = {2: 'e', 4: 'f', 8: 'd'}

def _get_int_format(size, n, endian, signed):
    if size not in (1, 2, 4, 8):
        raise ValueError("integer size '{}' not supported".format(size))

    if endian not in _endians:
        raise ValueError("endian '{}' is not recognized".format(endian))

    if signed:
        return _endians[endian] + str(n) + _signed_int_formats[size]
    else:
        return _endians[endian] + str(n) +  _unsigned_int_formats[size]

def _get_float_format(size, n, endian):
    if size not in (2, 4, 8):
        raise ValueError("float size '{}' not supported".format(size))

    if endian not in _endians:
        raise ValueError("endian '{}' is not recognized".format(endian))

    return _endians[endian] + str(n) +  _float_formats[size]

class StructIO(io.BytesIO):
    def __init__(self, b=b'', endian='little', encoding='utf-8', errors='ignore'):
        super().__init__(b)
        self.endian = endian
        self.encoding = encoding
        self.errors = errors

    @property
    def buffer(self):
        return self.getvalue()

    @buffer.setter
    def buffer(self, b):
        self.seek(0)
        self.write(b)
        self.truncate()
        self.seek(0)

    def __len__(self):
        position = self.tell()
        length = self.seek(0, 2)
        self.seek(position)
        return length

    def __eq__(self, other):
        return self.getvalue() == other.getvalue()

    def _get_endian(self, endian):
        if endian is None:
            return self.endian
        else:
            return endian

    def copy(self):
        return StructIO(self.getvalue(), self.endian, self.encoding, self.errors)

    def clear(self):
        self.seek(0)
        self.truncate()

    def find(self, b):
        return self.getvalue().find(b, self.tell())

    def index(self, b):
        return self.getvalue().index(b, self.tell())

    def read_bool(self):
        return self.read(1) != b'\x00'

    def write_bool(self, boolean):
        if boolean:
            return self.write(b'\x01')
        else:
            return self.write(b'\x00')

    def read_bits(self):
        number = self.read(1)[0]
        return [number >> i & 1 for i in range(8)]

    def write_bits(self, bits):
        return self.write(sum(bits[i] << i for i in range(8)).to_bytes(1))

    def read_int(self, size, endian=None, signed=False):
        return int.from_bytes(self.read(size), self._get_endian(endian), signed=signed)

    def write_int(self, number, size, endian=None, signed=False):
        return self.write(number.to_bytes(size, self._get_endian(endian), signed=signed))

    def read_ints(self, size, n, endian=None, signed=False):
        return struct.unpack(_get_int_format(size, n, self._get_endian(endian), signed), self.read(size * n))

    def write_ints(self, numbers, size, endian=None, signed=False):
        return self.write(struct.pack(_get_int_format(size, len(numbers), self._get_endian(endian), signed), *numbers))

    def read_float(self, size, endian=None):
        return struct.unpack(_get_float_format(size, 1, self._get_endian(endian)), self.read(size))[0]

    def write_float(self, number, size, endian=None):
        return self.write(struct.pack(_get_float_format(size, 1, self._get_endian(endian)), number))

    def read_floats(self, size, n, endian=None):
        return struct.unpack(_get_float_format(size, n, self._get_endian(endian)), self.read(size * n))

    def write_floats(self, numbers, size, endian=None):
        return self.write(struct.pack(_get_float_format(size, len(numbers), self._get_endian(endian)), *numbers))

    def read_str(self, length):
        return self.read(length).decode(self.encoding, errors=self.errors)

    def write_str(self, string):
        return self.write(string.encode(self.encoding, errors=self.errors))

    def read_cstr(self):
        start = self.tell()
        end = self.find(b'\x00')

        if end == -1:
            raise ValueError('null termination not found')

        string = self.read_str(end - start)
        self.seek(1, 1)
        return string

    def write_cstr(self, string):
        return self.write_str(string) + self.write(b'\x00')

    def skip_cstr(self):
        end = self.find(b'\x00')

        if end == -1:
            raise ValueError('null termination not found')

        return self.seek(end + 1)

    def read_pstr(self, size, endian=None):
        return self.read_str(self.read_int(size, endian))

    def write_pstr(self, string, size, endian=None):
        b = string.encode(self.encoding, errors=self.errors)
        return self.write_int(len(b), size, endian) + self.write(b)

    def skip_pstr(self, size, endian=None):
        return self.seek(self.read_int(size, endian), 1)

    def read_7bint(self):
        number = 0
        i = 0

        byte = self.read(1)[0]
        while byte > 127:
            number += (byte & 0b01111111) << (7 * i)
            i += 1

            byte = self.read(1)[0]

        number += byte << (7 * i)

        return number

    def write_7bint(self, number):
        length = 0

        while number > 127:
            length += self.write((number & 0b01111111 | 0b10000000).to_bytes(1))
            number >>= 7

        length += self.write(number.to_bytes(1))

        return length

    def skip_7bint(self):
        while self.read(1)[0] > 127:
            pass

        return self.tell()