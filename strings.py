from dbpf import *

def unpack_str(file):
    file.seek(0)
    
    content = {}
    content['file name'] = read_str(file)
    file.seek(64)
    content['format code'] = read_int(file, 2)
    
    if content['format code'] != 0xFFFD and content['format code'] != 0xFFFF:
        raise NotSupportedError('format code 0x{:04X} is not supported'.format(content['format code']))
    
    count = read_int(file, 2)
    
    content['languages'] = {}
    for i in range(count):
        language_code = read_int(file, 1)
        
        if language_code not in content['languages']:
            content['languages'][language_code] = []
            
        content['languages'][language_code].append(read_str(file))
        file.seek(search_file(file, b'\x00') + 1)
        
    file.seek(0)
    return content
    
def pack_str(content):
    file = BytesIO()
    write_str(file, content['file name'])
    write_int(file, 0, 64 - len(content['file name']))
    write_int(file, content['format code'], 2)
    write_int(file, sum(len(values) for values in content['languages'].values()), 2)
    
    for language_code, values in content['languages'].items():
        for value in values:
            write_int(file, language_code, 1)
            write_str(file, value, null_term=True)
            file.write(b'\x00')
            
    file.seek(0)
    return file