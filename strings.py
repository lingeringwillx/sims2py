from dbpf import *

def unpack_str(entry):
    decompress(entry)
    
    content = {}
    content['type'] = entry.type
    content['group'] = entry.group
    content['instance'] = entry.instance
    
    if 'resource' in entry:
        content['resource'] = entry.resource
        
    content['file name'] = entry.read_str()
    
    entry.seek(64)
    content['format code'] = entry.read_int(2)
    
    if content['format code'] != 0xFFFD and content['format code'] != 0xFFFF:
        raise NotSupportedError('format code 0x{:04X} is not supported'.format(content['format code']))
        
    count = entry.read_int(2)
    
    content['languages'] = {}
    for i in range(count):
        language_code = entry.read_int(1)
        
        if language_code not in content['languages']:
            content['languages'][language_code] = []
            
        content['languages'][language_code].append(entry.read_str())
        entry.seek(entry.find(b'\x00') + 1)
        
    entry.seek(0)
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
            
    if 'resource' in content:
        return Entry(content['type'], content['group'], content['instance'], content['resource'], content['file name'], file.read_all())
    else:
        return Entry(content['type'], content['group'], content['instance'], name=content['file name'], content=file.read_all())