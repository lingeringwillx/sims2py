## Purpose
1- To make it easier to access and read the game's data.

2- To enable quick script editing of the game's files.

## Getting Started
**Requirements:** Requires Windows and Python 3.2 or higher.

**Installation:** Download the build and place it in a folder named 'dbpf'. Outside the folder, create a python file and write `import dbpf` to import the library.

**Compilation:**
If you want to compile the C library yourself, you will need Mingw-w64 to be installed in your system.

To compile the library, run the compile.bat file.

## Functions

List of functions provided by the library:

-----

### Type Conversions

**bytes2int(b, endian='little', signed=False)**

Converts bytes object *b* to an integer. The endian can be specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**int2bytes(n, numbytes, endian='little', signed=False)**

Converts integer *n* to a bytes object. The endian can be specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**bytes2float(b, endian='little')**

Converts bytes object *b* to a float. The endian can be specified with the *endian* argument.

**float2bytes(n, endian='little')**

Converts float *n* to a bytes object. The endian can be specified with the *endian* argument.

**bytes2str(b)**

Converts *b* to a string.

**str2bytes(s, null_term=False)**

Converts string *s* to a bytes object. if *null_term* is set to True, then a null termination will be appended to the end.

**pstr2str(b, numbytes)**

Converts a bytes object *b* in the pascal string format into a string. The number of bytes containing the string's length can be specified with *numbytes*. The function will read up to the length specified in the first *numbytes* and ignore the rest.

**str2pstr(s, numbytes)**

convert string *s* into a bytes object in the pascal string format. The number of bytes that would contain the length of the string can be specified with *numbytes*.

**bstr2str(b)**

Converts a bytes object *b* in the [7-bit string](https://modthesims.info/wiki.php?title=7BITSTR) format into a string. The function will read up to the length specified in the first few bytes and ignore the rest of the bytes object.

**str2bstr(s)**

convert string *s* into a bytes object in the 7-bit string format.

-----

### File IO

**read_int(file, numbytes, endian='little', signed=False)**

Reads *numbytes* from *file* and converts it into a signed integer. The endian can be specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**write_int(file, number, numbytes, endian='little', signed=False)**

Converts *number* into a bytes object with length *numbytes* and endian *endian*, then writes it into *file*. The *signed* argument is used to specify whether the integer is signed or not.

**read_float(file, endian='little')**

Reads the next 4 bytes from *file* and converts them into a float. The endian can be specified with the *endian* argument.

**write_float(file, number, endian='little')**

Converts *number* into a bytes object with endian *endian*, then writes it into *file*.

**read_str(file, length=0)**

Reads a string from *file*. If the length is larger than zero, then it reads *length* bytes from *file* and returns the string. Otherwise, it keeps reading until it reaches a null termination and returns the string. The function expects a *BytesIO* file.

**write_str(file, string, null_term=False)**

Writes *string* into *file*. if *null_term* is set to True, then a null termination is also written to the file.

**read_pstr(file, numbytes)**

Reads a Pascal string from *file* and returns it. *numbytes* indicates how many bytes are used for the string's length in *file*.

**write_pstr(file, string, numbytes)**

Writes *string* to *file* as a Pascal string. *numbytes* indicates how many bytes are to be used for the string's length in *file*.

**read_7bstr(file)**

Reads a [7-bit string](https://modthesims.info/wiki.php?title=7BITSTR) from *file* and returns it as a string object.

**write_7bstr(file, string)**

Writes *string* into *file* in the 7-bit string format.

-----

### File Utils

**read_all(file)**

Reads all of the content of *file*.

**write_all(file, buffer)**

Overwrites the entire file with bytes object *buffer*.

**overwrite(file, bytes_sequence, start, size=0)**

Deletes the portion between *start* and *start + size* from *file*, and appends *bytes_sequence* in it's place.

**search_file(file, bytes_sequence, start=-1, n=1)**

Searches *file* for *bytes_sequence*. If *start* is specified then the file will be searched from *start*, otherwise it will be searched from it's current position. Returns the location in which the *nth* occurrence of *bytes_sequence* can be found, returns -1 if it's not found. The function expects a *BytesIO* file.

**get_size(file)**

Returns the size/length of *file*

-----

### Package Utils

**create_package()**

Creates a dictionary containing the data necessary to make an empty package file.

**read_package(file_path)**

Reads a package file from the provided *file_path* and returns a dictionary containing its data. For information on the dictionary, check the [dictionaries](#dictionaries) section.

**write_package(package, file_path)**

Converts the dictionary *package* into a package file and writes it to a file with the provided *file_path*.

**copy_package(package)**

Creates a copy of *package* and returns it.

**copy_header(header)**

creates a copy of *header* and returns it.

**create_entry(type_id, group_id, instance_id, resource_id=None, name='', content=b'', compressed=False)**

creates an entry containing the provided arguments.

**copy_entry(entry)**

creates a copy of *entry* and returns it.

**compress(entry)**

Compresses the content of *entry*. If the content of *entry* is already compressed, then nothing happens. Raises a *CompressionError* if compression fails. Returns a reference to *entry*.

**decompress(entry)**

Decompresses the content of *entry*. If the content of *entry* is already decompressed, then nothing happens. Raises a *CompressionError* if decompression fails. Returns a reference to *entry*.

**partial_decompress(entry, size=-1)**

Decompresses *entry* up to *size*. If *size* is not specified, then the whole file will decompressed. Returns a BytesIO object containing the decompressed bytes. Unlike the *decompress* function, this function does not overwrite the contents of *entry*.

**search(entries, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, file_name='', get_first=False)**

Searches the package's files for the desired type, group, instance, or resource, returns a list of the indices of the entries matching the criteria. if any of the arguments is set equal to -1 then the the function will ignore that specific argument. If *file_name* is specified, then the function will check if the names of supported file types contain *file_name*. If *get_first* is set to *True*, then the function will directly return a list containing the first index that it finds.

**build_index(entries)**

Returns an index that enables faster searching of *entries* using the *index_search* function. The returned index does NOT get updated when making changes to *entries* after the function is called.

**index_search(index, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, file_name='')**

Similar to the *search* function, but uses the index created by *build_index* for faster searching.

**print_tgi(entry)**

Displays the type, group, and instance of *entry*, as will as the name of *entry* if it has a name.

**read_file_name(entry)**

Reads the file name of *entry* for supported file types. Returns the name of the file if the file's type is supported, otherwise returns an empty sting.

**write_file_name(entry)**

Writes *entry['name']* to *entry['content']*. Only works with supported file types.

**unpack_str(file)**

Converts the files that use the [STR](#STR-dict) format into a dictionary. *file* needs to decompressed before passing it to the function. Throws an *NotSupportedError* if an STR resource with an unsupported format code is passed to the function. Currently only format codes 0xFFFD and 0xFFFF are supported. Other formats don't show up often in the game's code. The function does not unpack the description accompanying each string in the files.

**pack_str(content)**

Converts dictionaries created by the *unpack_str* function into a BytesIO file. Returns the file.

**unpack_cpf(file)**

Converts the files that use the [CPF](#CPF-dict) format into a dictionary. *file* needs to decompressed before passing it to the function.

**pack_cpf(content)**

Converts dictionaries created by the *unpack_cpf* function into a BytesIO file. Returns the file.

## Dictionaries
Structure of dictionaries created by this script:

#### package (dict)
Dictionary containing *header* and *entries*

-----

#### header (dict)

**'major version'** (int): Equal to 1.

**'minor version'** (int): Equal to 1.

**'major user version'** (int): Equal to 0.

**'minor user version'** (int): Equal to 0.

**'flags'** (int): Not known.

**'created date'** (int)

**'modified date'** (int)

**'index major version'** (int): Equal to 7.

**'index entry count'** (int): The number of entries in the file.

**'index location'** (int): The location of the file index.

**'index size'** (int): The length of the index.

**'hole index entry count'** (int): The number of holes in the file.

**'hole index location'** (int): The location of the holes index in the file.

**'hole index size'** (int): The length of the holes index.

**'index minor version'** (int): The index version, between 0 and 2.

**'remainder'** (bytes): What remains of the header.

-----

#### entries (list of dicts)
Each element in this list contains the following:

**'type'** (int): Entry type.

**'group'** (int): Entry group.

**'instance'** (int): Entry instance.

**'resource'** (int): Entry resource, only exists if the *index minor version* of the *header* is 2.

**'content'** (BytesIO): File-like object stored in memory containing the entry itself.

**'compressed'** (bool): Indicates whether the entry is compressed or not.

**'name'** (str): Contains the name of the entry for supported file types. Keep in mind that changing this value will not change the actual name in *'content'*. To write the new name to *'content'*, use the *write_file_name* function.

-----

#### STR (dict)
STR dictionaries created by the *unpack_str* function contain the following:

**'file name'** (str): The name of the entry

**'format code'** (int): The format code of the entry.

**'languages'** (dict of lists of strs): Dictionary containing a list of strings for each language, with the language's code being the key to the dictionary. Use the key *1* for the default English strings.

-----

#### CPF (dict)
CPF dictionaries created by the *unpack_cpf* function contain the following:

**'version'** (int)

**'entries'** (list of dicts): Each entry contains the following:

**'name'** (str): The name of the entry.

**'type'** (str): The name of the entry's type. Can be one of the following:

| Type | Name |
| --- | --- |
| uint | unsigned integer |
| str | string |
| float | float |
| bool | boolean |
| int | signed integer |

**'data'** (specified by *'type'*): the actual data in the entry.

## Resources
General information on DBPF (Package) files (A little dated): https://modthesims.info/wiki.php?title=DBPF

Useful image showing the game's file format: https://simswiki.info/images/e/e8/DBPF_File_Format_v1.1.png

Information on the various file types found in the package file's entries (A little dated): https://modthesims.info/wiki.php?title=List_of_Sims_2_Formats_by_Name

Information on the compression used by the game's files: https://modthesims.info/wiki.php?title=DBPF_Compression

Original code for the library I used for the compression and decompression code: www.moreawesomethanyou.com/smf/index.php/topic,8279.0.html

Notepad++ with the HEX-Editor plugin was useful for viewing the game's files: https://notepad-plus-plus.org/

SimPE also has a hex viewer, but it only shows you uncompressed entries: https://modthesims.info/showthread.php?t=630456

I used this tool to compare my edited files to the original files: https://github.com/Shelwien/cmp/
