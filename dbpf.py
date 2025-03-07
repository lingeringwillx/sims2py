from .structio import StructIO
import ctypes
import os
import sys

if sys.platform != 'win32':
    raise Exception('The dbpf library currently only works in Windows')

if sys.maxsize <= 2 ** 32:
    raise Exception('Requires a 64 bit system')

named_types = {0x42434F4E, 0x42484156, 0x4E524546, 0x4F424A44, 0x53545223, 0x54544142, 0x54544173, 0x424D505F, 0x44475250, 0x534C4F54, 0x53505232}
named_rcol_types = {0xFB00791E, 0x4D51F042, 0xE519C933, 0xAC4F8687, 0x7BA3838C, 0xC9C81B9B, 0xC9C81BA3, 0xC9C81BA9, 0xC9C81BAD, 0xED534136, 0xFC6EB1F7, 0x49596978, 0x1C4A276C}
named_cpf_types = {0x2C1FD8A1, 0x0C1FE246, 0xEBCF3E27}
lua_types = {0x9012468A, 0x9012468B}

class CompressionError(Exception): pass

qfs = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'qfs.dll'))

qfs.qfs_compress.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
qfs.qfs_compress.restype = ctypes.c_int

qfs.qfs_decompress.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
qfs.qfs_decompress.restype = ctypes.c_bool

class Header:
    def __init__(self):
        self.major_version = 1
        self.minor_version = 1
        self.major_user_version = 0
        self.minor_user_version = 0
        self.flags = 0
        self.created_date = 0
        self.modified_date = 0
        self.index_major_version = 7
        self.index_entry_count = 0
        self.index_location = 0
        self.index_size = 0
        self.hole_index_entry_count = 0
        self.hole_index_location = 0
        self.hole_index_size = 0
        self.index_minor_version = 2
        self.remainder = b'\x00' * 32

    def __str__(self):
        display = 'Header:\n'
        display += 'major version: {}\n'.format(self.major_version)
        display += 'minor version: {}\n'.format(self.minor_version)
        display += 'major user version: {}\n'.format(self.major_user_version)
        display += 'minor user version: {}\n'.format(self.minor_user_version)
        display += 'flags: {}\n'.format(self.flags)
        display += 'created date: {}\n'.format(self.created_date)
        display += 'modified date: {}\n'.format(self.modified_date)
        display += 'index major version: {}\n'.format(self.index_major_version)
        display += 'index entry count: {}\n'.format(self.index_entry_count)
        display += 'index location: {}\n'.format(self.index_location)
        display += 'index size: {}\n'.format(self.index_size)
        display += 'hole index entry count: {}\n'.format(self.hole_index_entry_count)
        display += 'hole index location: {}\n'.format(self.hole_index_location)
        display += 'hole index size: {}\n'.format(self.hole_index_size)
        display += 'index minor version: {}'.format(self.index_minor_version)

        return display

    def copy(self):
        header = Header()
        for key, value in vars(self).items():
            setattr(header, key, value)

        return header

class Entry(StructIO):
    def __init__(self, type_id, group_id, instance_id, resource_id=0, location=None, size=None, name='', content=b'', compressed=False):
        super().__init__(content)
        self.type = type_id
        self.group = group_id
        self.instance = instance_id
        self.resource = resource_id
        self.name = name
        self.compressed = compressed
        self._location = location
        self._size = size

    def __str__(self):
        if self.name == '':
            name_display = ''
        else:
            name_display = '{}\n'.format(self.name)

        return name_display + 'Type: 0x{:08X}, Group: 0x{:08X}, Instance: 0x{:08X}, Resource: 0x{:08X}'.format(self.type, self.group, self.instance, self.resource)

    def copy(self):
        return Entry(self.type, self.group, self.instance, self.resource, name=self.name, content=self.buffer, compressed=self.compressed)

    #using C++ library from moreawesomethanyou
    def compress(self):
        if not self.compressed and self.type != 0xE86B1EEF:
            src = self.buffer
            src_len = len(src)
            dst_len = src_len - 1 #should be smaller, otherwise keep it uncompressed
            dst = (ctypes.c_char * dst_len)()

            dst_len = qfs.qfs_compress(src, src_len, dst, dst_len)

            if dst_len:
                self.buffer = dst[:dst_len]
                self.compressed = True

        return self

    #using C++ library from moreawesomethanyou
    def decompress(self):
        if self.compressed:
            src = self.buffer
            src_len = len(src)

            self.seek(6)
            dst_len = self.read_int(3, 'big')
            self.seek(0)

            dst = (ctypes.c_char * dst_len)()
            success = qfs.qfs_decompress(src, src_len, dst, dst_len)

            if success:
                self.buffer = dst
                self.compressed = False
            else:
                raise CompressionError('Could not decompress the file')

        return self

    def read_name(self):
        try:
            if self.type in named_types:
                self.decompress()
                self.name = self.read(64).rstrip(b'x\00').decode('utf-8', errors='ignore')

            elif self.type in named_rcol_types:
                self.decompress()
                location = self.find(b'\x0bcSGResource')

                if location != -1:
                    self.seek(location + 20)
                    self.name = self.read_str(self.read_7bint())

            elif self.type in named_cpf_types:
                self.decompress()
                location = self.find(b'\x18\xea\x8b\x0b\x04\x00\x00\x00name')

                if location != -1:
                    self.seek(location + 12)
                    self.name = self.read_pstr(4)

            elif self.type in lua_types:
                self.decompress()
                self.seek(4)
                self.name = self.read_pstr(4)

            else:
                self.name = ''

        except:
            self.name = ''

        self.seek(0)
        return self.name

class Package:
    def __init__(self):
        self.path = ''
        self.header = Header()
        self.entries = []

    def copy(self):
        package = Package()
        package.path = self.path
        package.header = self.header.copy()
        package.entries = [entry.copy() for entry in self.entries]

        return package

    def unpack(path, decompress=False, read_names=False):
        with open(path, 'rb') as file:
            self = Package()
            self.path = path

            #read header
            stream = StructIO(file.read(96))
            stream.seek(4)

            self.header.major_version = stream.read_int(4)
            self.header.minor_version = stream.read_int(4)
            self.header.major_user_version = stream.read_int(4)
            self.header.minor_user_version = stream.read_int(4)
            self.header.flags = stream.read_int(4)
            self.header.created_date = stream.read_int(4)
            self.header.modified_date = stream.read_int(4)
            self.header.index_major_version = stream.read_int(4)
            self.header.index_entry_count = stream.read_int(4)
            self.header.index_location = stream.read_int(4)
            self.header.index_size = stream.read_int(4)
            self.header.hole_index_entry_count = stream.read_int(4)
            self.header.hole_index_location = stream.read_int(4)
            self.header.hole_index_size = stream.read_int(4)
            self.header.index_minor_version = stream.read_int(4)
            self.header.remainder = stream.read(32)

            #read index
            self.entries = []

            file.seek(self.header.index_location)
            stream = StructIO(file.read(self.header.index_size))

            for i in range(self.header.index_entry_count):
                if self.header.index_minor_version == 2:
                    type_id, group_id, instance_id, resource_id, location, size = stream.read_ints(4, 6)
                else:
                    type_id, group_id, instance_id, location, size = stream.read_ints(4, 5)
                    resource_id = 0

                self.entries.append(Entry(type_id, group_id, instance_id, resource_id, location, size))

            #read entries
            for entry in self.entries:
                file.seek(entry._location)
                entry.buffer = file.read(entry._size)

        #read CLST
        #using a set for speed
        clst_entries = set()
        results = search(self.entries, 0xE86B1EEF)

        if len(results) > 0:
            clst = results[0]

            if self.header.index_minor_version == 2:
                entry_size = 20
            else:
                entry_size = 16

            for i in range(len(clst) // entry_size):
                if self.header.index_minor_version == 2:
                    type_id, group_id, instance_id, resource_id, uncompressed_size = clst.read_ints(4, 5)
                else:
                    type_id, group_id, instance_id, uncompressed_size = clst.read_ints(4, 4)
                    resource_id = 0

                clst_entries.add((type_id, group_id, instance_id, resource_id))

            clst.seek(0)

        #check if compressed
        for entry in self.entries:
            entry.compressed = (entry.type, entry.group, entry.instance, entry.resource) in clst_entries

        #decompress entries
        if decompress:
            for entry in self.entries:
                try:
                    entry.decompress()
                except CompressionError:
                    pass

        #read entry names
        if read_names:
            for entry in self.entries:
                try:
                    entry.read_name()
                except CompressionError:
                    pass

        return self

    def pack_into(self, path, compress=False):
        #compress entries
        if compress:
            for entry in self.entries:
                entry.compress()

        #check for repeated compressed entries, decompress repeats
        compressed_entries = {}
        for entry in self.entries:
            if entry.compressed:
                tgir = (entry.type, entry.group, entry.instance, entry.resource)

                if tgir in compressed_entries:
                    entry.decompress()
                    compressed_entries[tgir].decompress()
                else:
                    compressed_entries[tgir] = entry

        #make CLST
        results = search(self.entries, 0xE86B1EEF)
        compressed_entries = [entry for entry in self.entries if entry.compressed]

        if len(results) > 0:
            for result in results:
                self.entries.remove(result)

        if len(compressed_entries) > 0:
            clst = Entry(0xE86B1EEF, 0xE86B1EEF, 0x286B1F03, 0x00000000)

            for compressed_entry in compressed_entries:
                #uncompressed size is written in big endian
                compressed_entry.seek(6)
                uncompressed_size = compressed_entry.read_int(3, 'big')

                if self.header.index_minor_version == 2:
                    clst.write_ints((compressed_entry.type, compressed_entry.group, compressed_entry.instance, compressed_entry.resource, uncompressed_size), 4)
                else:
                    clst.write_ints((compressed_entry.type, compressed_entry.group, compressed_entry.instance, uncompressed_size), 4)

                compressed_entry.seek(0)

            self.entries.append(clst)

        #use index minor version 2?
        if self.header.index_minor_version != 2:
            for entry in self.entries:
                if entry.resource != 0:
                    self.header.index_minor_version = 2
                    break

        temp_path = path.rsplit('.')[0] + '.tmp'

        with open(temp_path, 'wb') as file:
            stream = StructIO()

            #write header
            stream.write(b'DBPF')
            stream.write_int(self.header.major_version, 4)
            stream.write_int(self.header.minor_version, 4)
            stream.write_int(self.header.major_user_version, 4)
            stream.write_int(self.header.minor_user_version, 4)
            stream.write_int(self.header.flags, 4)
            stream.write_int(self.header.created_date, 4)
            stream.write_int(self.header.modified_date, 4)
            stream.write_int(self.header.index_major_version, 4)
            stream.write(b'\x00' * 24) #update later
            stream.write_int(self.header.index_minor_version, 4)
            stream.write(self.header.remainder)

            file.write(stream.buffer)

            #write entries and update location and size
            for entry in self.entries:
                entry._location = file.tell()
                file.write(entry.buffer)
                entry._size = file.tell() - entry._location

            stream.clear()

            #write index
            for entry in self.entries:
                if self.header.index_minor_version == 2:
                    stream.write_ints((entry.type, entry.group, entry.instance, entry.resource, entry._location, entry._size), 4)
                else:
                    stream.write_ints((entry.type, entry.group, entry.instance, entry._location, entry._size), 4)

            index_start = file.tell()
            file.write(stream.buffer)
            index_end = file.tell()

            stream.clear()

            #update header info
            self.header.index_entry_count = len(self.entries)
            self.header.index_location = index_start
            self.header.index_size = index_end - index_start
            self.header.hole_index_entry_count = 0
            self.header.hole_index_location = 0
            self.header.hole_index_size = 0

            stream.write_int(self.header.index_entry_count, 4)
            stream.write_int(self.header.index_location, 4)
            stream.write_int(self.header.index_size, 4)

            file.seek(36)
            file.write(stream.buffer)

        os.replace(temp_path, path)
        self.path = path

def search(entries, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, entry_name=''):
    entry_name = entry_name.lower()

    results = []

    for entry in entries:
        if type_id != -1 and type_id != entry.type:
            continue

        if group_id != -1 and group_id != entry.group:
            continue

        if instance_id != -1 and instance_id != entry.instance:
            continue

        if resource_id != -1 and resource_id != entry.resource:
            continue

        if entry_name != '' and entry_name not in entry.name.lower():
            continue

        results.append(entry)

    return results