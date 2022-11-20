from io import BytesIO
import struct

class MemoryIO(BytesIO):
    def __len__(self):
        return len(self.getvalue())
        
    def copy(self):
        return MemoryIO(self.getvalue())
        
    def read_all(self):
        self.seek(0)
        return self.getvalue()
        
    def write_all(self, buffer):
        self.seek(0)
        length = self.write(buffer)
        self.truncate()
        self.seek(0)
        return length
        
    def read_int(self, numbytes, endian='little', signed=False):
        return int.from_bytes(self.read(numbytes), endian, signed=signed)
        
    def write_int(self, number, numbytes, endian='little', signed=False):
        return self.write(number.to_bytes(numbytes, endian, signed=signed))
        
    def read_float(self):
        return struct.unpack('<f', self.read(4))[0]
            
    def write_float(self, number):
        return self.write(struct.pack('<f', number))   
            
    def read_str(self, length=-1):
        if length > -1:
            return self.read(length).decode('utf-8', errors='ignore')
            
        else:
            end = self.find(b'\x00')
            
            if end == -1:
                raise EOFError('Null termination not found')
                
            start = self.tell()
            string = self.read(end - start).decode('utf-8', errors='ignore')
            self.seek(1, 1)
            return string
            
    def write_str(self, string, null_term=False):
        length = self.write(string.encode('utf-8', errors='ignore'))
        
        if null_term:
            self.write(b'\x00')
            return length + 1
        else:
            return length
            
    def read_pstr(self, numbytes):
        return self.read_str(self.read_int(numbytes))
        
    def write_pstr(self, string, numbytes):
        return self.write_int(len(string), numbytes) + self.write_str(string)
        
    def read_7bstr(self):
        length = 0
        i = 0
        
        byte = self.read_int(1)
        while byte & 0b10000000 != 0:
            length |= (byte & 0b01111111) << (7 * i)
            i += 1
            
            byte = self.read_int(1)
            
        length |= byte << (7 * i)
        
        return self.read_str(length)
        
    def write_7bstr(self, string):
        length = len(string)
        i = 0
        
        while length > 127:
            self.write_int(length & 0b01111111 | 0b10000000, 1) 
            length >>= 7
            i += 1
            
        self.write_int(length, 1)
        i += 1
        
        return self.write_str(string) + i
        
    def _append(self, writer, args):
        start = self.tell()
        buffer = self.read()
        self.seek(start)
        length = writer(*args)
        self.write(buffer)
        self.seek(start + length)
        return length        
        
    def append_int(self, number, numbytes, endian='little', signed=False):
        return self._append(self.write_int, (number, numbytes, endian, signed))
        
    def append_float(self, number):
        return self._append(self.write_float, (number,))
        
    def append_str(self, string, null_term=False):
        return self._append(self.write_str, (string, null_term))
        
    def append_pstr(self, string, numbytes):
        return self._append(self.write_pstr, (string, numbytes))
        
    def append_7bstr(self, string):
        return self._append(self.write_7bstr, string)
        
    def _overwrite(self, reader, reader_args, writer, writer_args):
        start = self.tell()
        reader(*reader_args)
        buffer = self.read()
        self.seek(start)
        length = writer(*writer_args)
        self.write(buffer)
        self.truncate()
        self.seek(start + length)
        return length
        
    def overwrite_str(self, string, length=-1, null_term=False):
        return self._overwrite(self.read_str, (length,), self.write_str, (string, null_term))
        
    def overwrite_pstr(self, string, numbytes):
        return self._overwrite(self.read_pstr, (numbytes,), self.write_pstr, (string, numbytes))
	    
    def overwrite_7bstr(self, string):
        return self._overwrite(self.read_7bstr, (), self.write_7bstr, (string,))
        
    def delete(self, length):
        current_position = self.tell()
        
        if current_position - length < 0:
            length = current_position
            
        start = current_position - length
        
        buffer = self.read()
        self.seek(start)
        self.write(buffer)
        self.truncate()
        self.seek(start)
        
        return length
        
    def find(self, bytes_sequence, n=1):
        start = self.tell()
        content = self.getvalue()
        
        location = content.find(bytes_sequence, start)
        
        for i in range(1, n):
            location = content.find(bytes_sequence, location + 1)
            
            if location == -1:
                break
                
        return location