from dbpf import *

def unpack_cpf(file):
    content = {}
    file.seek(4)
    content['version'] = file.read_int(2)
    count = file.read_int(4)
    
    content['entries'] = []
    for i in range(count):
        entry = {}
        type_code = file.read_int(4)
        entry['name'] = file.read_pstr(4)
        
        if type_code == 0xEB61E4F7:
            entry['type'] = 'uint'
            entry['data'] = file.read_int(4)
            
        elif type_code == 0x0B8BEA18:
            entry['type'] = 'str'
            entry['data'] = file.read_pstr(4)
            
        elif type_code == 0xABC78708:
            entry['type'] = 'float'
            entry['data'] = file.read_float()
            
        elif type_code == 0xCBA908E1:
            entry['type'] = 'bool'
            entry['data'] = file.read_int(1) != 0
            
        elif type_code == 0x0C264712:
            entry['type'] = 'int'
            entry['data'] = file.read_int(4)
            
        content['entries'].append(entry)
        
    file.seek(0)
    return content
    
def pack_cpf(content):
    file = MemoryIO()
    file.write_int(0xCBE750E0, 4)
    file.write_int(content['version'], 2)
    file.write_int(len(content['entries']), 4)
    
    for entry in content['entries']:
        if entry['type'] == 'uint':
            file.write_int(0xEB61E4F7, 4)
            file.write_pstr(entry['name'], 4)
            file.write_int(entry['data'], 4)
            
        elif entry['type'] == 'str':
            file.write_int(0x0B8BEA18, 4)
            file.write_pstr(entry['name'], 4)
            file.write_pstr(entry['data'], 4)
            
        elif entry['type'] == 'float':
            file.write_int(0xABC78708, 4)
            file.write_pstr(entry['name'], 4)
            file.write_float(entry['data'])
            
        elif entry['type'] == 'bool':
            file.write_int(0xCBA908E1, 4)
            file.write_pstr(entry['name'], 4)
            
            if entry['data']:
                file.write_int(1, 1)
            else:
                file.write_int(0, 1)
                
        elif entry['type'] == 'int':
            file.write_int(0x0C264712, 4)
            file.write_pstr(entry['name'], 4)
            file.write_int(entry['data'], 4, signed=True)
            
    file.seek(0)
    return file