from io import BytesIO
import ctypes
import os
import string
import struct
import sys

"""
Structure of dictionaries created by this script:
package: {header: dict, entries: list of dicts}

header:
'major version' = int #1
'minor version' = int #1
'major user version' = int #0
'minor user version' = int #0
'flags' = int #unknown
'created date' = int #not important
'modified date' = int #not important
'index major version' = int #7
'index entry count' = int #number of entries in file
'index location' = int #location of file index
'index size' = int #length of index
'hole index entry count' = int #number oh holes in file
'hole index location' = int #location of hole index
'hole index size' = int #length of hole index
'index minor version' = int #index version, between 0 and 2
'remainder' = 32 bytes #what remains of the header

entry:
'type': int #entry type
'group': int #entry group
'instance': int #entry instance
'resource': int #entry resource, only exists if the index minor version is 2
'content' = BytesIO #file-like object stored in memory containing the entry itself
'compressed' = bool #indicates whether the entry is compressed or not
'name' = str #name of entry
"""

if sys.platform != 'win32':
    raise Exception('The dbpf library currently only works in Windows')
    
if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2):
    raise Exception('The dbpf library requires Python 3.2 or higher')
    
named_types = {0x42434F4E, 0x42484156, 0x4E524546, 0x4F424A44, 0x53545223, 0x54544142, 0x54544173, 0x424D505F, 0x44475250, 0x534C4F54, 0x53505232}
named_rcol_types = {0xFB00791E, 0x4D51F042, 0xE519C933, 0xAC4F8687, 0x7BA3838C, 0xC9C81B9B, 0xC9C81BA3, 0xC9C81BA9, 0xC9C81BAD, 0xED534136, 0xFC6EB1F7, 0x49596978, 0x1C4A276C}
named_cpf_types = {0x2C1FD8A1, 0x0C1FE246, 0xEBCF3E27}
lua_types = {0x9012468A, 0x9012468B}

is_64bit = sys.maxsize > 2 ** 32

if is_64bit:
    clib = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(__file__),'dbpf64.dll'))
else:
    clib = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(__file__),'dbpf32.dll'))
    
clib.decompress.restype = ctypes.c_bool

class RepeatKeyError(Exception): pass
class CompressionError(Exception): pass
class NameLengthError(Exception): pass
class NotSupportedError(Exception): pass

def bytes2int(b, endian='little', signed=False):
    return int.from_bytes(b, endian, signed=signed)
    
def int2bytes(n, numbytes, endian='little', signed=False):
    return n.to_bytes(numbytes, endian, signed=signed)
    
def bytes2float(b, endian='little'):
    if endian == 'little':
        return struct.unpack('<f', b)[0]
    elif endian == 'big':
        return struct.unpack('>f', b)[0]
    else:
        raise ValueError("Unexpected endian '{}'".format(endian))
        
def float2bytes(n, endian='little'):
    if endian == 'little':
        return struct.pack('<f', n)
    elif endian == 'big':
        return struct.pack('>f', n)
    else:
        raise ValueError("Unexpected endian '{}'".format(endian))
        
def bytes2str(b):
        return b.decode('utf-8')
        
def str2bytes(s, null_term=False):
    b = s.encode('utf-8')
    
    if null_term:
        b += b'\x00'

    return b
    
def pstr2str(b, numbytes):
    length = bytes2int(b[:numbytes])
    start = numbytes
    end = start + length
    return bytes2str(b[start:end])
    
def str2pstr(s, numbytes):
    return int2bytes(len(s), numbytes) + str2bytes(s)

def bstr2str(b):
    length = 0
    i = 0

    byte = b[i]
    while byte & 0b10000000 != 0:
        length |= (byte & 0b01111111) << (7 * i)
        i += 1
        
        byte = b[i]
        
    length |= byte << (7 * i)
    start = i + 1
    end = start + length
    return bytes2str(b[start:end])
    
def str2bstr(s):
    length = len(s)
    b = b''
    
    while length > 127:
        b += int2bytes(length & 0b01111111 | 0b10000000, 1)
        length >>= 7
        
    b += int2bytes(length, 1)
    b += str2bytes(s)
    
    return b

def read_int(file, numbytes, endian='little', signed=False):
    return int.from_bytes(file.read(numbytes), endian, signed=signed)
    
def write_int(file, number, numbytes, endian='little', signed=False):
    return file.write(number.to_bytes(numbytes, endian, signed=signed))
    
def read_float(file, endian='little'):
    if endian == 'little':
        return struct.unpack('<f', file.read(4))[0]
    elif endian == 'big':
        return struct.unpack('>f', file.read(4))[0]
    else:
        raise ValueError("Unexpected endian '{}'".format(endian))
        
def write_float(file, number, endian='little'):
    if endian == 'little':
        return file.write(struct.pack('<f', number))
    elif endian == 'big':
        return file.write(struct.pack('>f', number))
    else:
        raise ValueError("Unexpected endian '{}'".format(endian))    
        
def read_str(file, length=0):
    if length > 0:
        return file.read(length).decode('utf-8', errors='ignore')
        
    else:
        content = file.getvalue()
        start = file.tell()
        end = content.find(b'\x00', start)
        
        if end == -1:
            raise EOFError('Null termination not found')
        
        file.seek(end + 1)
        return content[start:end].decode('utf-8', errors='ignore')
        
def write_str(file, string, null_term=False):
    length = file.write(string.encode('utf-8'))
    
    if null_term:
        file.write(b'\x00')
        return length + 1
    else:
        return length
        
def read_pstr(file, numbytes):
    return file.read(read_int(file, numbytes)).decode('utf-8')

def write_pstr(file, string, numbytes):
    write_int(file, len(string), numbytes)
    return file.write(string.encode('utf-8')) + numbytes
    
def read_7bstr(file):
    length = 0
    i = 0
    
    byte = read_int(file, 1)
    while byte & 0b10000000 != 0:
        length |= (byte & 0b01111111) << (7 * i)
        i += 1
        
        byte = read_int(file, 1)
        
    length |= byte << (7 * i)
    
    return file.read(length).decode('utf-8')
    
def write_7bstr(file, string):
    length = len(string)
    i = 0
    
    while length > 127:
        write_int(file, length & 0b01111111 | 0b10000000, 1) 
        length >>= 7
        i += 1
        
    write_int(file, length, 1)
    i += 1
    
    return file.write(string.encode('utf-8')) + i
    
def read_all(file):
    return file.getvalue()
    
def write_all(file, buffer):
    file.seek(0)
    length = file.write(buffer)
    file.truncate()
    file.seek(0)
    return length
    
def overwrite(file, bytes_sequence, start, size=0):
    file.seek(start + size)
    buffer = file.read()
    file.seek(start)
    file.write(bytes_sequence)
    file.write(buffer)
    file.truncate()
    file.seek(0)
    
def search_file(file, bytes_sequence, start=-1, n=1):
    if start == -1:
        start = file.tell()
        
    content = file.getvalue()
    location = content.find(bytes_sequence, start)
    for i in range(1, n):
        location = content.find(bytes_sequence, location + 1)
        
        if location == -1:
            break
            
    return location
    
def get_size(file):
    current_position = file.tell()
    
    file.seek(0, 2)
    size = file.tell()
    
    file.seek(current_position)
    
    return size
    
def create_package():
    header = {};
    header['major version'] = 1
    header['minor version'] = 1
    header['major user version'] = 0
    header['minor user version'] = 0
    header['flags'] = 0
    header['created date'] = 0
    header['modified date'] = 0
    header['index major version'] = 7
    header['index entry count'] = 0
    header['index location'] = 0
    header['index size'] = 0
    header['hole index entry count'] = 0
    header['hole index location'] = 0
    header['hole index size'] = 0
    header['index minor version'] = 2
    
    header['remainder'] = b''

    for i in range(32):
        header['remainder'] += b'\x00'
    
    return {'header': header, 'entries': []}
    
def read_package(file_path):
    with open(file_path, 'rb') as fs:
        file = BytesIO(fs.read())
        
    #read header
    header = {};
    
    file.seek(4)
    header['major version'] = read_int(file, 4)
    header['minor version'] = read_int(file, 4)
    header['major user version'] = read_int(file, 4)
    header['minor user version'] = read_int(file, 4)
    header['flags'] = read_int(file, 4)
    header['created date'] = read_int(file, 4)
    header['modified date'] = read_int(file, 4)
    header['index major version'] = read_int(file, 4)
    header['index entry count'] = read_int(file, 4)
    header['index location'] = read_int(file, 4)
    header['index size'] = read_int(file, 4)
    header['hole index entry count'] = read_int(file, 4)
    header['hole index location'] = read_int(file, 4)
    header['hole index size'] = read_int(file, 4)
    header['index minor version'] = read_int(file, 4)
    header['remainder'] = file.read(32)
    
    #read index
    entries = []
    
    file.seek(header['index location'])
    for i in range(header['index entry count']):
        entry = {}
        
        #using int.from_bytes and file.read instead of read_int to avoid the function call overhead
        entry['type'] = int.from_bytes(file.read(4), 'little')
        entry['group'] = int.from_bytes(file.read(4), 'little')
        entry['instance'] = int.from_bytes(file.read(4), 'little')
        
        if header['index minor version'] == 2:
            entry['resource'] = int.from_bytes(file.read(4), 'little')
            
        location = int.from_bytes(file.read(4), 'little')
        size = int.from_bytes(file.read(4), 'little')
        
        position = file.tell()
        file.seek(location)
        entry['content'] = BytesIO(file.read(size))
        file.seek(position)
        
        entries.append(entry)
        
    #make list of index entries
    #the entries list is for checking if the file is compressed later, just for increasing execution speed
    #so that we don't need to spend time converting the CLST entries to integers
    index_entries = []
    
    if header['index minor version'] == 2:
        size = 16
    else:
        size = 12
        
    file.seek(header['index location'])
    for i in range(header['index entry count']):
        index_entries.append(file.read(size))
        file.seek(8, 1)
        
    #read CLST
    #using a set for speed
    clst_entries = set()
    results = search(entries, 0xE86B1EEF, get_first=True)
    
    if len(results) > 0:
        i = results[0]
        clst = entries[i]
        file_size = get_size(clst['content'])
        
        if header['index minor version'] == 2:
            entry_size = 20
            tgi_size = 16
        else:
            entry_size = 16
            tgi_size = 12
        
        clst['content'].seek(0)
        for i in range(file_size // entry_size):
            entry = clst['content'].read(tgi_size)
            
            if entry not in clst_entries:
                clst_entries.add(entry)
            else:
                raise RepeatKeyError('Two entries with matching type, group, and instance found')
                
            clst['content'].seek(4, 1)
            
        clst['content'].seek(0)
    
    #check if compressed
    for index_entry, entry in zip(index_entries, entries):
        entry['compressed'] = False
        
        if index_entry in clst_entries:
            entry['content'].seek(4)
            
            #entries can be in the CLST file even if they're not compressed
            #so a second check for compression would be good
            if entry['content'].read(2) == b'\x10\xfb':
                entry['compressed'] = True
                
            entry['content'].seek(0)
            
    #read file names
    for entry in entries:
        try:
            entry['name'] = read_file_name(entry)
        except CompressionError:
            entry['name'] = ''
        
    return {'header': header, 'entries': entries} 
    
def write_package(package, file_path):
    header = package['header']
    entries = package['entries']
    
    #update file names
    #for entry in entries:
    #try:
    #    write_file_name(entry)
    #except CompressionError:
    #    pass
    
    #use index minor version 2?
    if header['index minor version'] != 2:
        for entry in entries:
            if 'resource' in entry:
                header['index minor version'] = 2
                break
                
    with open(file_path, 'wb') as file:
        file.seek(0)
        
        #write header
        file.write(b'DBPF')
        write_int(file, header['major version'], 4)
        write_int(file, header['minor version'], 4)
        write_int(file, header['major user version'], 4)
        write_int(file, header['minor user version'], 4)
        write_int(file, header['flags'], 4)
        write_int(file, header['created date'], 4)
        write_int(file, header['modified date'], 4)
        write_int(file, header['index major version'], 4)
        write_int(file, header['index entry count'], 4)
        write_int(file, header['index location'], 4)
        write_int(file, header['index size'], 4)
        write_int(file, header['hole index entry count'], 4)
        write_int(file, header['hole index location'], 4)
        write_int(file, header['hole index size'], 4)
        write_int(file, header['index minor version'], 4)
        
        file.write(header['remainder'])
        
        #make CLST
        results = search(entries, 0xE86B1EEF, get_first=True)
        compressed_files = [entry for entry in entries if entry['compressed']]
        
        if len(results) > 0:
            entries.pop(results[0])
            
        if len(compressed_files) > 0:
            clst = {}
            clst['type'] = 0xE86B1EEF
            clst['group'] = 0xE86B1EEF
            clst['instance'] = 0x286B1F03
            
            if header['index minor version'] == 2:
                clst['resource'] = 0x00000000
                
            clst['content'] = BytesIO()
            
            for compressed_file in compressed_files:
                write_int(clst['content'], compressed_file['type'], 4)
                write_int(clst['content'], compressed_file['group'], 4)
                write_int(clst['content'], compressed_file['instance'], 4)
                
                if header['index minor version'] == 2:
                    if 'resource' in compressed_file:
                        write_int(clst['content'], compressed_file['resource'], 4)
                    else:
                        write_int(clst['content'], 0, 4)
                        
                #uncompressed size is written in big endian?
                compressed_file['content'].seek(6)
                uncompressed_size = read_int(compressed_file['content'], 3, 'big')
                write_int(clst['content'], uncompressed_size, 4)
                
            entries.append(clst)
            
        #write entries
        for entry in entries:
            #get new location to put in the index later
            entry['location'] = file.tell()
            
            file.write(read_all(entry['content']))
            
            #get new file size to put in the index later
            entry['size'] = file.tell() - entry['location']
            
        #write index
        index_start = file.tell()
        
        for entry in entries:
            write_int(file, entry['type'], 4)
            write_int(file, entry['group'], 4)
            write_int(file, entry['instance'], 4)
            
            if header['index minor version'] == 2:
                if 'resource' in entry:
                    write_int(file, entry['resource'], 4)
                else:
                    write_int(file, 0, 4)
                    
            write_int(file, entry['location'], 4)
            write_int(file, entry['size'], 4)
            
        index_end = file.tell()
        
        file.truncate()
        
        #update header index info, clear holes index info
        file.seek(36)
        write_int(file, len(entries), 4) #index entry count
        write_int(file, index_start, 4) #index location
        write_int(file, index_end - index_start, 4) #index size
        write_int(file, 0, 12) #hole index entries
        
#copy.deepcopy from the standard library takes too much time, better to write our own functions
def copy_package(package):
    package_copy = {}
    package_copy['header'] = copy_header(package['header'])
    package_copy['entries'] = [copy_entry(entry) for entry in package['entries']]
    
    return package_copy
    
def copy_header(header):
    header_copy = {}
    for key, value in header.items():
        header_copy[key] = value
        
    return header_copy
    
def create_entry(type_id, group_id, instance_id, resource_id=None, name='', content=b'', compressed=False):
    entry = {}
    entry['type'] = type_id
    entry['group'] = group_id
    entry['instance'] = instance_id
    
    if resource_id is not None:
        entry['resource'] = resource_id
        
    entry['name'] = name
    entry['content'] = BytesIO(content)
    entry['compressed'] = compressed
    
    return entry
    
def copy_entry(entry):
    entry_copy = {}
    entry_copy['type'] = entry['type']
    entry_copy['group'] = entry['group']
    entry_copy['instance'] = entry['instance']
    
    if 'resource' in entry:
        entry_copy['resource'] = entry['resource']
        
    current_position = entry['content'].tell()
    entry_copy['content'] = BytesIO(read_all(entry['content']))
    entry['content'].seek(current_position)
    
    entry_copy['compressed'] = entry['compressed']
    
    return entry_copy
    
#using C++ library from moreawesomethanyou   
def compress(entry):
    if entry['compressed'] or entry['type'] == 0xE86B1EEF:
        return entry
        
    else:
        src = read_all(entry['content'])
        src_len = len(src)
        dst = ctypes.create_string_buffer(src_len)
        
        dst_len = clib.try_compress(src, src_len, dst)
        
        if dst_len > 0:
            write_all(entry['content'], dst.raw[:dst_len])
            entry['compressed'] = True
            
            return entry
            
        else:
            raise CompressionError('Could not compress the file')
            
#using C++ library from moreawesomethanyou 
def decompress(entry):
    if entry['compressed']:
        src = read_all(entry['content'])
        compressed_size = len(src)
        
        entry['content'].seek(6)
        uncompressed_size = read_int(entry['content'], 3, 'big')
        
        dst = ctypes.create_string_buffer(uncompressed_size)
        success = clib.decompress(src, compressed_size, dst, uncompressed_size, False)
        
        entry['content'].seek(0)
        
        if success:
            write_all(entry['content'], dst.raw)
            entry['compressed'] = False
            
            return entry
            
        else:
            raise CompressionError('Could not decompress the file')
            
    else:
        return entry
        
def partial_decompress(entry, size=-1):
    if entry['compressed']:
        src = read_all(entry['content'])  
        compressed_size = len(src)
        
        entry['content'].seek(6)
        uncompressed_size = read_int(entry['content'], 3, 'big')
        
        if size == -1 or size >= uncompressed_size:
            size = uncompressed_size
            truncate = False
            
        else:
            truncate = True
            
        dst = ctypes.create_string_buffer(size)
        success = clib.decompress(src, compressed_size, dst, size, truncate)
        
        entry['content'].seek(0)
        
        if success:
            return BytesIO(dst.raw)
        else:
            raise CompressionError('Could not decompress the file')
            
    else:
        #if size is -1, then read(size) will read the whole file
        entry['content'].seek(0)
        dst = entry['content'].read(size)
        entry['content'].seek(0)
        return BytesIO(dst)
        
def search(entries, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, file_name='', get_first=False):
    file_name = file_name.lower()
    
    indices = []
    for i, entry in enumerate(entries):
        if type_id != -1 and type_id != entry['type']:
            continue
            
        if group_id != -1 and group_id != entry['group']:
            continue
            
        if instance_id != -1 and instance_id != entry['instance']:
            continue
            
        if resource_id != -1 and resource_id != entry['resource']:
            continue
            
        if file_name != '' and file_name not in entry['name'].lower():
            continue
            
        indices.append(i)
        
        if get_first:
            return indices
            
    return indices
    
#for faster searching
def build_index(entries):
    index = {}
    index['types'] = {}
    index['groups'] = {}
    index['instances'] = {}
    index['resources'] = {}
    index['names index'] = {}
    index['names list'] = []
    
    for c in string.printable:
        index['names index'][c] = set()
        
    for i, entry in enumerate(entries):
        if entry['type'] not in index['types']:
            index['types'][entry['type']] = set()
            
        index['types'][entry['type']].add(i)
        
        if entry['group'] not in index['groups']:
            index['groups'][entry['group']] = set()
            
        index['groups'][entry['group']].add(i)
            
        if entry['instance'] not in index['instances']:
            index['instances'][entry['instance']] = set()
            
        index['instances'][entry['instance']].add(i)
            
        if 'resource' in entry:
            if entry['resource'] not in index['resources']:
                index['resources'][entry['resource']] = set()
                
            index['resources'][entry['resource']].add(i)
            
        name = entry['name'].lower()
        index['names list'].append(name)
        
        if name != '':
            for char in name:
                index['names index'][char].add(i)
                
    return index
    
#faster search
def index_search(index, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, file_name=''):
    results = []
    keys = ['types', 'groups', 'instances', 'resources']
    values = [type_id, group_id, instance_id, resource_id]
    
    for key, value in zip(keys, values):
        if value == -1:
            pass
        elif value in index[key]:
            results.append(index[key][value])
        else:
            return []
        
    if len(results) > 0:
        results = set.intersection(*results)
        
    if file_name != '':
        file_name = file_name.lower()
        names_set = (index['names index'][char] for char in file_name)
        
        if len(results) > 0:
            results = results.intersection(*names_set)
        else:
            results = set.intersection(*names_set)
            
        if len(file_name) > 1:
            return [i for i in results if file_name in index['names list'][i]]
            
    return list(results)
    
def print_tgi(entry):
    if entry['name'] != '':
        print(entry['name'])
        
    if 'resource' in entry:
        print('Type: 0x{:08X}, Group: 0x{:08X}, Instance: 0x{:08X}, Resource: 0x{:08X}'.format(entry['type'], entry['group'], entry['instance'], entry['resource']))
    else:
        print('Type: 0x{:08X}, Group: 0x{:08X}, Instance: 0x{:08X}'.format(entry['type'], entry['group'], entry['instance']))
        
def read_file_name(entry):
    if entry['type'] in named_types:
        return partial_decompress(entry, 64).read().rstrip(b'\x00').decode('utf-8')
        
    elif entry['type'] in named_rcol_types:
        file = partial_decompress(entry, 255)
        location = search_file(file, b'cSGResource')
        
        if location == -1:
            return ''
        else:
            file.seek(location + 19)
            return read_7bstr(file)
            
    elif entry['type'] in named_cpf_types:
        file = partial_decompress(entry)
        location = search_file(file, b'name')
        
        if location == -1:
            return ''
        else:
            file.seek(location + 4)
            return read_pstr(file, 4)
            
    elif entry['type'] in lua_types:
        file = partial_decompress(entry, 255)
        file.seek(4)
        return read_pstr(file, 4)        
        
    elif entry['type'] == 0x46574156:
        file = partial_decompress(entry)
        file.seek(64)
        return file.read().rstrip(b'\x00').decode('utf-8')
        
    else:
        return ''
        
def write_file_name(entry):
    was_compressed = False
    
    if entry['type'] in named_types:
        if entry['compressed']:
            decompress(entry)
            was_compressed = True
            
            if len(entry) <= 64:
                entry['content'].seek(0)
                write_str(entry['content'], entry['name'])
                write_int(entry['content'], 0, 64 - len(entry['name']))
                entry['content'].seek(0)
            else:
                raise NameLengthError("file name '{}' is longer than expected".format(entry['name']))
                
    elif entry['type'] in named_rcol_types:
        if entry['compressed']:
            decompress(entry)
            was_compressed = True
            
        location = search_file(entry['content'], b'cSGResource')
        
        if location != -1:
            location += 19
            entry['content'].seek(location)
            length = len(read_7bstr(entry['content'])) + 1
            
            if length > 127 + 1:
                length += 1
                
            overwrite(entry['content'], str2bstr(entry['name']), location, length) 
            entry['content'].seek(0)
            
    elif entry['type'] in named_cpf_types:
        if entry['compressed']:
            decompress(entry)
            was_compressed = True
            
        location = search_file(entry['content'], b'name')
        
        if location != -1:
            location += 4
            entry['content'].seek(location)
            length = read_int(entry['content'], 4) + 4
            
            overwrite(entry['content'], str2pstr(entry['name'], 4), location, length) 
            entry['content'].seek(0)
            
    elif entry['type'] in lua_types:
        if entry['compressed']:
            decompress(entry)
            was_compressed = True
            
        entry['content'].seek(4)
        length = read_int(entry['content'], 4) + 4
        
        overwrite(entry['content'], str2pstr(entry['name'], 4), 4, length) 
        entry['content'].seek(0)
        
    elif entry['type'] == 0x46574156:
        if entry['compressed']:
            decompress(entry)
            was_compressed = True
            
        entry['content'].seek(64)
        write_str(entry['content'], entry['name'], null_term=True)
        entry['content'].truncate()
        entry['content'].seek(0)
        
    if was_compressed:
        compress(entry)