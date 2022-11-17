from dbpf import *

def unpack_str(file):
    file.seek(0)
    
    content = {}
    content['file name'] = file.read_str()
    file.seek(64)
    content['format code'] = file.read_int(2)
    
    if content['format code'] != 0xFFFD and content['format code'] != 0xFFFF:
        raise NotSupportedError('format code 0x{:04X} is not supported'.format(content['format code']))
        
    count = file.read_int(2)
    
    content['languages'] = {}
    for i in range(count):
        language_code = file.read_int(1)
        
        if language_code not in content['languages']:
            content['languages'][language_code] = []
            
        content['languages'][language_code].append(file.read_str())
        file.seek(file.find(b'\x00') + 1)
        
    file.seek(0)
    return content
    
def pack_str(content):
    file = MemoryIO()
    file.write_str(content['file name'])
    file.write_int(0, 64 - len(content['file name']))
    file.write_int(content['format code'], 2)
    file.write_int(sum(len(values) for values in content['languages'].values()), 2)
    
    for language_code, values in content['languages'].items():
        for value in values:
            file.write_int(language_code, 1)
            file.write_str(value, null_term=True)
            file.write(b'\x00')
            
    file.seek(0)
    return file