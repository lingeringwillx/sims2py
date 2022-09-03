from copy import deepcopy as copy
from io import BytesIO
import ctypes
import sys

"""
Structure of dictionaries created by this script:
package: {header: dict, subfiles: list of dicts}

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

subfile: #aka entries
'type': int #entry type
'group': int #entry group
'instance': int #entry instance
'resource': int #entry resource, only exists if the index minor version is 2
'content' = BytesIO #file-like object stored in memory containing the entry itself
'compressed' = bool #indicates whether the entry is compressed or not
"""

if sys.platform != 'win32':
    raise Exception('The dbpf library currently only works in Windows')
    
if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
    raise Exception('The dbpf library requires Python 3.7 or higher')
    
is_64bit = sys.maxsize > 2 ** 32

if is_64bit:
    clib = ctypes.cdll.LoadLibrary('./dbpf64.dll')
else:
    clib = ctypes.cdll.LoadLibrary('./dbpf32.dll')
    
clib.decompress.restype = ctypes.c_bool

def read_int(file, numbytes, endian='little'):
    return int.from_bytes(file.read(numbytes), endian)
    
def write_int(file, num, numbytes, endian='little'):
    return file.write(num.to_bytes(numbytes, endian))
    
def read_str(file):
    content = b''
    buff = file.read(1)
    
    while buff != b'\x00':
        content += buff
        buff = file.read(1)
        
    return content.decode('utf-8')
    
def write_str(file, string):
    return file.write(string.encode('utf-8'))
    
def get_size(file):
    current_position = file.tell()
    
    file.seek(0, 2)
    size = file.tell()
    
    file.seek(current_position)
    
    return size
    
def read_package(file):
    file.seek(0)
    file = BytesIO(file.read())

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
    subfiles = []
    
    file.seek(header['index location'])
    for i in range(header['index entry count']):
        subfile = {}
        
        #using int.from_bytes and file.read instead of read_int to avoid the function call overhead
        subfile['type'] = int.from_bytes(file.read(4), 'little')
        subfile['group'] = int.from_bytes(file.read(4), 'little')
        subfile['instance'] = int.from_bytes(file.read(4), 'little')
        
        if header['index minor version'] == 2:
            subfile['resource'] = int.from_bytes(file.read(4), 'little')
            
        location = int.from_bytes(file.read(4), 'little')
        size = int.from_bytes(file.read(4), 'little')
        
        position = file.tell()
        file.seek(location)
        subfile['content'] = BytesIO(file.read(size))
        file.seek(position)
        
        subfiles.append(subfile)
        
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
    results = search(subfiles, 0xE86B1EEF, get_first=True)
    
    if len(results) > 0:
        i = results[0]
        clst_file = subfiles[i]
        length = get_size(clst_file['content'])
        
        if header['index minor version'] == 2:
            entry_size = 20
            tgi_size = 16
        else:
            entry_size = 16
            tgi_size = 12
        
        clst_file['content'].seek(0)
        for i in range(length // entry_size):
            entry = clst_file['content'].read(tgi_size)
            
            if entry not in clst_entries:
                clst_entries.add(entry)
            else:
                raise Exception('Two entries with matching type, group, and instance found')
                
            clst_file['content'].seek(4, 1)
    
    #check if compressed
    for index_entry, subfile in zip(index_entries, subfiles):
        subfile['compressed'] = False
        
        if index_entry in clst_entries:
            subfile['content'].seek(4)
            if subfile['content'].read(2) == b'\x10\xfb':
                subfile['compressed'] = True
                
            subfile['content'].seek(0)
                
    return {'header': header, 'subfiles': subfiles} 
    
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
    
    return {'header': header, 'subfiles': []}
    
def write_package(file, package):
    header = package['header']
    subfiles = package['subfiles']
    
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
    compressed_files = [subfile for subfile in subfiles if subfile['compressed']]
    
    if len(compressed_files) > 0:
        clst_file = {}
        clst_file['type'] = 0xE86B1EEF
        clst_file['group'] = 0xE86B1EEF
        clst_file['instance'] = 0x286B1F03
        
        if header['index minor version'] == 2:
            clst_file['resource'] = 0x00000000
        
        clst_file['content'] = BytesIO()
        
        for compressed_file in compressed_files:
            write_int(clst_file['content'], compressed_file['type'], 4)
            write_int(clst_file['content'], compressed_file['group'], 4)
            write_int(clst_file['content'], compressed_file['instance'], 4)
            
            if header['index minor version'] == 2:
                write_int(clst_file['content'], compressed_file['resource'], 4)
                
            #uncompressed size is written in big endian?
            compressed_file['content'].seek(6)
            uncompressed_size = read_int(compressed_file['content'], 3, 'big')
            write_int(clst_file['content'], uncompressed_size, 4)
            
    #write subfiles
    for subfile in subfiles:
        if subfile['type'] != 0xE86B1EEF:
            #get new location to put in the index later
            subfile['location'] = file.tell()
        
            subfile['content'].seek(0)
            file.write(subfile['content'].read())
        
            #get new file size to put in the index later
            subfile['size'] = file.tell() - subfile['location']
    
    #write CLST
    if len(compressed_files) > 0:
        clst_file['location'] = file.tell()   
    
        clst_file['content'].seek(0)
        file.write(clst_file['content'].read())
        
        clst_file['size'] = file.tell() - clst_file['location']
    
    #write index
    index_start = file.tell()
    
    for subfile in subfiles:
        if subfile['type'] != 0xE86B1EEF:
            write_int(file, subfile['type'], 4)
            write_int(file, subfile['group'], 4)
            write_int(file, subfile['instance'], 4)
            
            if header['index minor version'] == 2:
                write_int(file, subfile['resource'], 4)    
                
            write_int(file, subfile['location'], 4)
            write_int(file, subfile['size'], 4)
            
    if len(compressed_files) > 0:
        write_int(file, clst_file['type'], 4)
        write_int(file, clst_file['group'], 4)
        write_int(file, clst_file['instance'], 4)
        
        if header['index minor version'] == 2:
            write_int(file, subfile['resource'], 4)   
            
        write_int(file, clst_file['location'], 4)
        write_int(file, clst_file['size'], 4)
        
    index_end = file.tell()
    
    file.truncate()
    
    #update header index info, clear holes index info
    file.seek(36)
    write_int(file, len(subfiles), 4) #index entry count
    write_int(file, index_start, 4) #index location
    write_int(file, index_end - index_start, 4) #index size
    write_int(file, 0, 12) #hole index entries
    
def search(subfiles, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, get_first=False):
    indices = []
    for i, subfile in enumerate(subfiles):
        type_match = type_id == -1 or type_id == subfile['type']
        
        if not type_match:
            continue
        
        group_match = group_id == -1 or group_id == subfile['group']
        
        if not group_match:
            continue
        
        instance_match = instance_id == -1 or instance_id == subfile['instance']
        
        if not instance_match:
            continue
        
        resource_match = resource_id == -1 or resource_id == subfile['resource']
        
        if not resource_match:
            continue
        
        indices.append(i)
        
        if get_first:
            return indices
        
    return indices
    
#using C++ library from moreawesomethanyou   
def compress(subfile):
    if subfile['compressed']:
        subfile['content'].seek(0)
        return copy(subfile)
        
    else:
        subfile['content'].seek(0)
        
        src = subfile['content'].read()
        src_len = get_size(subfile['content'])
        dst = ctypes.create_string_buffer(src_len)
        
        dst_len = clib.try_compress(src, src_len, dst)
        
        if dst_len > 0:
            new_subfile = copy(subfile)
            new_subfile['content'] = BytesIO(dst.raw[:dst_len])
            new_subfile['compressed'] = True
            return new_subfile
            
        else:
            raise Exception('Could not compress the file')

#using C++ library from moreawesomethanyou 
def decompress(subfile):
    if subfile['compressed']:
        subfile['content'].seek(0)
        compressed_size = read_int(subfile['content'], 4)
        subfile['content'].seek(6)
        uncompressed_size = read_int(subfile['content'], 3, 'big')
        
        subfile['content'].seek(0)
        src = subfile['content'].read()    
        dst = ctypes.create_string_buffer(uncompressed_size)
        
        success = clib.decompress(src, compressed_size, dst, uncompressed_size, False)
        
        if success:
            new_subfile = copy(subfile)
            new_subfile['content'] = BytesIO(dst.raw)
            new_subfile['compressed'] = False
            return new_subfile
            
        else:
            raise Exception('Could not decompress the file')
        
    else:
        subfile['content'].seek(0)
        return copy(subfile)
        
def print_TGI(subfile):
    if 'resource' in subfile:
        print('Type: 0x{:08X}, Group: 0x{:08X}, Instance: 0x{:08X}, Resource: 0x{:08X}'.format(subfile['type'], subfile['group'], subfile['instance'], subfile['resource']))
    else:
        print('Type: 0x{:08X}, Group: 0x{:08X}, Instance: 0x{:08X}'.format(subfile['type'], subfile['group'], subfile['instance']))
        
#for faster searching
def build_index(subfiles):
    index = {}
    index['types'] = {}
    index['groups'] = {}
    index['instances'] = {}
    index['resources'] = {}
    
    for i, subfile in enumerate(subfiles):
        if subfile['type'] not in index['types']:
            index['types'][subfile['type']] = set()
            
        index['types'][subfile['type']].add(i)
        
        if subfile['group'] not in index['groups']:
            index['groups'][subfile['group']] = set()
            
        index['groups'][subfile['group']].add(i)
            
        if subfile['instance'] not in index['instances']:
            index['instances'][subfile['instance']] = set()
            
        index['instances'][subfile['instance']].add(i)
            
        if 'resource' in subfile:
            if subfile['resource'] not in index['resources']:
                index['resources'][subfile['resource']] = set()
                
            index['resources'][subfile['resource']].add(i)
        
    return index
    
#faster search
def index_search(index, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1):
    keys = ['types', 'groups', 'instances', 'resources']
    values = [type_id, group_id, instance_id, resource_id]
    
    return set.intersection(*[index[key][value] for key, value in zip(keys, values) if value != -1])