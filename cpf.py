from dbpf import *

def unpack_cpf(file):
    content = {}
    file.seek(4)
    content['version'] = read_int(file, 2)
    count = read_int(file, 4)
    
    content['entries'] = []
    for i in range(count):
        entry = {}
        type_code = read_int(file, 4)
        entry['name'] = read_pstr(file, 4)
        
        if type_code == 0xEB61E4F7:
            entry['type'] = 'uint'
            entry['data'] = read_int(file, 4)
            
        elif type_code == 0x0B8BEA18:
            entry['type'] = 'str'
            entry['data'] = read_pstr(file, 4)
            
        elif type_code == 0xABC78708:
            entry['type'] = 'float'
            entry['data'] = read_float(file)
            
        elif type_code == 0xCBA908E1:
            entry['type'] = 'bool'
            entry['data'] = read_int(file, 1) != 0
            
        elif type_code == 0x0C264712:
            entry['type'] = 'int'
            entry['data'] = read_int(file, 4)
            
        content['entries'].append(entry)
            
    return content
    
def pack_cpf(content):
    file = BytesIO()
    write_int(file, 0xCBE750E0, 4)
    write_int(file, content['version'], 2)
    write_int(file, len(content['entries']), 4)
    
    for entry in content['entries']:
        if entry['type'] == 'uint':
            write_int(file, 0xEB61E4F7, 4)
            write_pstr(file, entry['name'], 4)
            write_int(file, entry['data'], 4)
            
        elif entry['type'] == 'str':
            write_int(file, 0x0B8BEA18, 4)
            write_pstr(file, entry['name'], 4)
            write_pstr(file, entry['data'], 4)
            
        elif entry['type'] == 'float':
            write_int(file, 0xABC78708, 4)
            write_pstr(file, entry['name'], 4)
            write_float(file, entry['data'])
            
        elif entry['type'] == 'bool':
            write_int(file, 0xCBA908E1, 4)
            write_pstr(file, entry['name'], 4)
            
            if entry['data']:
                write_int(file, 1, 1)
            else:
                write_int(file, 0, 1)
                
        elif entry['type'] == 'int':
            write_int(file, 0x0C264712, 4)
            write_pstr(file, entry['name'], 4)
            write_int(file, entry['data'], 4, signed=True)
            
    file.seek(0)
    return file