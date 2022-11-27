# Purpose

1- To make it easier to access and read the game's data.

2- To enable quick script editing of the game's files.

# Getting Started

**Requirements:** Requires Windows and Python 3.2 or higher.

**Installation:** Download the build and place it in a folder named 'dbpf'. Outside the folder, create a python file and write `import dbpf` to import the library.

**Compilation:** If you want to compile the C library yourself, you will need Mingw-w64 to be installed in your system.

To compile the library, run the compile.bat file.

# Objects

## Package

Creates an object resembling the structure of a *.package* file.

### Attributes

**header** (Header): Contains the [header](#Header)

**entries** (list\[Entry]): Contains instances of [Entry](#Entry).

### Methods

**Package()**

Creates a Package object containing the data required to make an empty package file.

**Package.unpack(file_path)**

Static method. Reads a package file from the provided *file_path* and returns a *Package* object containing its data.

**pack_into(file_path)**

Converts the Package object into a package file and writes it to a file with the provided *file_path*.

**copy()**

Creates a copy of the package and returns it.

## Header

### Attributes

**major_version** (int): Equal to 1.

**minor_version** (int): Equal to 1.

**major_user_version** (int): Equal to 0.

**minor_user_version** (int): Equal to 0.

**flags** (int): Not known.

**created_date** (int)

**modified_date** (int)

**index_major_version** (int): Equal to 7.

**index_entry_count** (int): The number of entries in the file.

**index_location** (int): The location of the file index.

**index_size** (int): The length of the index.

**hole_index_entry_count** (int): The number of holes in the file.

**hole_index_location** (int): The location of the holes index in the file.

**hole_index_size** (int): The length of the holes index.

**index_minor_version** (int): The index version, between 0 and 2.

**remainder** (bytes): What remains of the header.

### Methods

**Header()**:

Creates a Header object containing the data of a package file's header.

**copy()**:

Creates a copy of the header and returns it.

## Entry

Inherits from [MemoryIO](#MemoryIO).

### Attributes

**type** (int): Entry type.

**group** (int): Entry group.

**instance** (int): Entry instance.

**resource** (int): Entry resource, only exists if the *index minor version* of the *header* is 2.

**compressed** (bool): Indicates whether the entry is compressed or not.

**name** (str): Contains the name of the entry for supported entry types. Keep in mind that changing this value will not change the actual name in the entry's content. To apply the new name to the entry, use the *write_name* function.

### Methods

**Entry(type_id, group_id, instance_id, resource_id=None, name='', content=b'', compressed=False)**

Creates an entry containing the provided arguments.

**copy()**

Creates a copy of *entry* and returns it.

**read_name()**

Reads the name of the entry from it's content and writes it to *name*. Returns the name of the entry if the entry's type is supported, otherwise returns an empty string.

**write_name()**

Writes the name of the entry in the *name* attribute to it's content. Only works with supported entry types.

## MemoryIO

File-like object stored in memory. Extends *io.BytesIO* from the standard library, which means that it has all of the basic methods of file-like objects, including *read*, *write*, *seek*, *tell*, and *truncate*.

### Methods

**MemoryIO(b='')**

Take bytes object *b* and returns a *MemoryIO* object containing *b*.

**\_\_len\_\_()**

Returns the size/length of the file.

**copy()**

creates a copy of the object and returns it.

**read_all()**

Reads and returns all of the content of the file.

**write_all(buffer)**

Overwrites the entire file with bytes object *buffer*.

**read_int(numbytes, endian='little', signed=False)**

Reads *numbytes* bytes from the file and converts it into an integer. The endian can be specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**write_int(number, numbytes, endian='little', signed=False)**

Converts *number* into a bytes object with length *numbytes* and endian *endian*, then writes it into the file. The *signed* argument is used to specify whether the integer is signed or not.

**append_int(number, numbytes, endian='little', signed=False)**

Same as *write_int* but appends the value to the file at the current position instead of overwriting existing bytes.

**read_float()**

Reads the next 4 bytes from the file and converts them into a float.

**write_float(number)**

Converts *number* into a bytes object then writes it into the file.

**append_float(number)**

Same as *write_float* but appends the value to the file at the current position instead of overwriting existing bytes.

**read_str(length=0)**

Reads a string from the file. If the length is larger than zero, then it reads *length* bytes from the file and returns the string. Otherwise, it keeps reading until it reaches a null termination and returns the string.

**write_str(string, null_term=False)**

Writes *string* into the file. if *null_term* is set to True, then a null termination is also written to the file.

**append_str(string, null_term=False)**

Same as *write_str* but appends the value to the file at the current position instead of overwriting existing bytes.

**overwrite_str(string, length=-1, null_term=False)**

Deletes the string existing at the current location, then writes *string* in it's place. if *length* is specified then the function will delete *length* bytes, otherwise it will delete all bytes until it encounters a null termination. if *null_term* is set to True, then a null termination is also written to the file.

**read_pstr(numbytes)**

Reads a Pascal string from the file and returns it. *numbytes* is used to specify how many bytes are used for the string's length in the file.

**write_pstr(string, numbytes)**

Writes *string* to the file as a Pascal string. *numbytes* is used to specify how many bytes are used for the string's length in the file.

**overwrite_pstr(string, numbytes)**

Deletes the existing Pascal string at the current position and writes *string* as a Pascal string in it's place. *numbytes* is used to specify how many bytes are used for the integer holding the string's length.

**append_pstr(string, numbytes)**

Same as *write_pstr* but appends the value to the file at the current position instead of overwriting existing bytes.

**read_7bstr()**

Reads a [7-bit string](https://modthesims.info/wiki.php?title=7BITSTR) from the file and returns it as a string object.

**write_7bstr(string)**

Writes *string* into the file in the 7-bit string format.

**append_7bstr(string)**

Same as *write_7bstr* but appends the value to the file at the current position instead of overwriting existing bytes.

**overwrite_7bstr(string)**

Deletes the 7-bit string existing at the current location and writes *string* as a 7-bit string in it's place.

**delete(length)**

Deletes *length* bytes from the file starting from *current position - length* to *current position*.

**find(bytes_sequence, n=1)**

Searches *file* for *bytes_sequence*. Returns the location in which the *nth* occurrence of *bytes_sequence* can be found, returns -1 if it's not found. Starts searching from the current position  in the buffer.

# Functions

**compress(entry)**

Compresses the content of *entry*. If the content of *entry* is already compressed, then nothing happens. Raises a *CompressionError* if compression fails. Returns a reference to *entry*.

**decompress(entry)**

Decompresses the content of *entry*. If the content of *entry* is already decompressed, then nothing happens. Raises a *CompressionError* if decompression fails. Returns a reference to *entry*.

**partial_decompress(entry, size=-1)**

Decompresses *entry* up to *size*. If *size* is not specified, then the whole file will decompressed. Returns a MemoryIO object containing the decompressed bytes. Unlike the *decompress* function, this function does not overwrite the contents of *entry*.

**search(entries, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, file_name='', get_first=False)**

Searches the package's files for the desired type, group, instance, or resource, returns a list of the indices of the entries matching the criteria. if any of the arguments is set equal to -1 then the the function will ignore that specific argument. If *file_name* is specified, then the function will check if the names of supported file types contain *file_name*. If *get_first* is set to *True*, then the function will directly return a list containing the first index that it finds.

**build_index(entries)**

Returns an index that enables faster searching of *entries* using the *index_search* function. The returned index does NOT get updated when making changes to *entries* after the function is called.

**index_search(index, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, file_name='')**

Similar to the *search* function, but uses the index created by *build_index* for faster searching.

**unpack_str(entry)**

Converts the entries that use the [STR](#STR-dict) format into a dictionary. Throws a *NotSupportedError* if a STR entry with an unsupported format code is passed to the function. Currently only format codes 0xFFFD and 0xFFFF are supported. Other formats don't show up often in the game's code. The function does not unpack the descriptions accompanying each string in the entries.

**pack_str(content)**

Converts dictionaries created by the *unpack_str* function into a MemoryIO file and returns the file.

**unpack_cpf(entry)**

Converts entries that use the [CPF](#CPF-dict) format into a dictionary.

**pack_cpf(content)**

Converts dictionaries created by the *unpack_cpf* function into a MemoryIO file and returns the file.

# Dictionaries

## STR (dict)
STR dictionaries created by the *unpack_str* function contain the following:

**'file name'** (str): The name of the entry

**'format code'** (int): The format code of the entry.

**'languages'** (dict of lists of strs): Dictionary containing a list of strings for each language, with the language's code being the key to the dictionary. Use the key 1 for the default English strings.

## CPF (dict)
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

# Resources
General information on DBPF (Package) files (A little dated): https://modthesims.info/wiki.php?title=DBPF

Useful image showing the game's file format: https://simswiki.info/images/e/e8/DBPF_File_Format_v1.1.png

Information on the various file types found in the package file's entries (A little dated): https://modthesims.info/wiki.php?title=List_of_Sims_2_Formats_by_Name

Information on the compression used by the game's files: https://modthesims.info/wiki.php?title=DBPF_Compression

Original code for the library I used for the compression and decompression code: www.moreawesomethanyou.com/smf/index.php/topic,8279.0.html

Notepad++ with the HEX-Editor plugin was useful for viewing the game's files: https://notepad-plus-plus.org/

SimPE also has a hex viewer, but it only shows you uncompressed entries: https://modthesims.info/showthread.php?t=630456

I used this tool to compare my edited files to the original files: https://github.com/Shelwien/cmp/
