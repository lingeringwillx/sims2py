from io import BytesIO

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
        
    def read_float(self, endian='little'):
        if endian == 'little':
            return struct.unpack('<f', self.read(4))[0]
        elif endian == 'big':
            return struct.unpack('>f', self.read(4))[0]
        else:
            raise ValueError("Unexpected endian '{}'".format(endian))
            
    def write_float(self, number, endian='little'):
        if endian == 'little':
            return self.write(struct.pack('<f', number))
        elif endian == 'big':
            return self.write(struct.pack('>f', number))
        else:
            raise ValueError("Unexpected endian '{}'".format(endian))    
            
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
        
    def write_pstr(self, string, numbytes, endian='little'):
        return self.write_int(len(string), numbytes, endian) + self.write_str(string)
        
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
        
    def append_int(self, number, numbytes, endian='little', signed=False):
        start = self.tell()
        buffer = self.read()
        self.seek(start)
        length = self.write_int(number, numbytes, endian='little', signed=False)
        self.write(buffer)
        self.seek(start + length)
        return length
        
    def append_float(self, number, endian='little'):
        start = self.tell()
        buffer = self.read()
        self.seek(start)
        length = self.write_float(self, number, endian='little')
        self.write(buffer)
        self.seek(start + length)
        return length
        
    def append_str(self, string, null_term=False):
        start = self.tell()
        buffer = self.read()
        self.seek(start)
        length = self.write_str(string, null_term)
        self.write(buffer)
        self.seek(start + length)
        return length
        
    def append_pstr(self, string, numbytes):
        start = self.tell()
        buffer = self.read()
        self.seek(start)
        length = self.write_pstr(string, numbytes)
        self.write(buffer)
        self.seek(start + length)
        return length
        
    def append_7bstr(self, string):
        start = self.tell()
        buffer = self.read()
        self.seek(start)
        length = self.write_7bstr(string)
        self.write(buffer)
        self.seek(start + length)
        return length
        
    def overwrite_str(self, string, length=-1, null_term=False):
        start = self.tell()
        self.read_str(length)
        buffer = self.read()
        self.seek(start)
        length = self.write_str(string, null_term)
        self.write(buffer)
        self.truncate()
        self.seek(start + length)
        return length
        
    def overwrite_pstr(self, string, numbytes):
        start = self.tell()
        length = self.read_int(numbytes)
        self.seek(length, 1)
        buffer = self.read()
        self.seek(start)
        length = self.write_pstr(string, numbytes)
        self.write(buffer)
        self.truncate()
        self.seek(start + length)
        return length
	
    def overwrite_7bstr(self, string):
        start = self.tell()
        self.read_7bstr()
        buffer = self.read()
        self.seek(start)
        self.write_7bstr(string)
        self.write(buffer)
        self.truncate()
        self.seek(start + length)
        return length
        
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