from dbpf import *

def unpack_cpf(entry):
    decompress(entry)
    
    content = {}
    content['type'] = entry.type
    content['group'] = entry.group
    content['instance'] = entry.instance
    
    if 'resource' in entry:
        content['resource'] = entry.resource
        
    id = entry.read_int(4)
    if id != 0xCBE750E0:
        raise NotSupportedError('Not a CPF file, could be an XML file')
        
    entry.seek(4)
    content['version'] = entry.read_int(2)
    count = entry.read_int(4)
    
    content['values'] = []
    for i in range(count):
        value = {}
        type_code = entry.read_int(4)
        value['name'] = entry.read_pstr(4)
        
        if type_code == 0xEB61E4F7:
            value['type'] = 'uint'
            value['data'] = entry.read_int(4)
            
        elif type_code == 0x0B8BEA18:
            value['type'] = 'str'
            value['data'] = entry.read_pstr(4)
            
        elif type_code == 0xABC78708:
            value['type'] = 'float'
            value['data'] = entry.read_float()
            
        elif type_code == 0xCBA908E1:
            value['type'] = 'bool'
            value['data'] = entry.read_int(1) != 0
            
        elif type_code == 0x0C264712:
            value['type'] = 'int'
            value['data'] = entry.read_int(4)
            
        content['values'].append(value)
        
    entry.seek(0)
    return content
    
def pack_cpf(content):
    file = MemoryIO()
    file.write_int(0xCBE750E0, 4)
    file.write_int(content['version'], 2)
    file.write_int(len(content['values']), 4)
    
    for value in content['values']:
        if value['type'] == 'uint':
            file.write_int(0xEB61E4F7, 4)
            file.write_pstr(value['name'], 4)
            file.write_int(value['data'], 4)
            
        elif value['type'] == 'str':
            file.write_int(0x0B8BEA18, 4)
            file.write_pstr(value['name'], 4)
            file.write_pstr(value['data'], 4)
            
        elif value['type'] == 'float':
            file.write_int(0xABC78708, 4)
            file.write_pstr(value['name'], 4)
            file.write_float(value['data'])
            
        elif value['type'] == 'bool':
            file.write_int(0xCBA908E1, 4)
            file.write_pstr(value['name'], 4)
            
            if value['data']:
                file.write_int(1, 1)
            else:
                file.write_int(0, 1)
                
        elif value['type'] == 'int':
            file.write_int(0x0C264712, 4)
            file.write_pstr(value['name'], 4)
            file.write_int(value['data'], 4, signed=True)
            
    if 'resource' in content:
        return Entry(content['type'], content['group'], content['instance'], content['resource'], content['file name'], file.read_all())
    else:
        return Entry(content['type'], content['group'], content['instance'], name=content['file name'], content=file.read_all())