## Purpose
1- To make it easier to access and read the game's data.

2- To enable quick script editing of the game's files.

## Documentation
### Getting Started
**Requirements:** Requires Windows and Python 3.2 or higher.

**Installation:** Download the build, then make a python file in the same directory as the library and write `import dbpf` to import the library.

**Compilation:**
If you want to compile the C library yourself, you will need the following:

1- MinGW

2- MinGW 64-bit

To compile the library, run the compile.bat file.

### Functions
**read_int(file, numbytes, endian='little', signed=False)**

Reads *numbytes* from *file* and converts it into a signed integer. The endian can be specified with the *endian* argument. The *signed* argument is used to specify whether the integer is signed or not.

**write_int(file, number, numbytes, endian='little', signed=False)**

Converts *number* into a bytes object with length *numbytes* and endian *endian*, then writes it into *file*. The *signed* argument is used to specify whether the integer is signed or not.

**read_float(file, endian='little')**

Reads the next 4 bytes from *file* and converts them into a float. The endian can be specified with the *endian* argument.

**write_float(file, number, endian='little')**

Converts *number* into a bytes object with endian *endian*, then writes it into *file*.

**read_str(file, length=0)**

Reads a string from *file*. If the length is larger than zero, then it reads *length* bytes from *file* and returns the string. Otherwise, it keeps reading until it reaches a null termination and returns the string.

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

**read_package(file_path)**

Reads a package file from the provided *file_path* and returns a dictionary containing its data. For information on the dictionary, check the [dictionaries](#dictionaries) section.

**create_package()**

Creates a dictionary containing the data necessary to make an empty package file.

**write_package(package, file_path)**

Converts the dictionary *package* into a package file and writes it to a file with the provided *file_path*.

**search(subfiles, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, file_name='', get_first=False)**

Searches the package's files for the desired type, group, instance, or resource, returns a list of the indices of the subfiles matching the criteria. if any of the arguments is set equal to -1 then the the function will ignore that specific argument. If *file_name* is specified, then the function will check if the names of supported file types contain *file_name*. If *get_first* is set to *True*, then the function will directly return a list containing the first index that it finds.

**copy_package(package)**

Creates a copy of *package* and returns it.

**copy_header(header)**

creates a copy of *header* and returns it.

**copy_subfile(subfile)**

creates a copy of *subfile* and returns it.

**get_size(file)**

Returns the size/length of *file*

**compress(subfile)**

Compresses the content of *subfile*. If the content of *subfile* is already compressed, then nothing happens. Raises a *CompressionError* if compression fails. Returns a reference to *subfile*.

**decompress(subfile)**

Decompresses the content of *subfile*. If the content of *subfile* is already decompressed, then nothing happens. Raises a *CompressionError* if decompression fails. Returns a reference to *subfile*.

**print_TGI(subfile)**

Displays the type, group, and instance of a *subfile*.

**build_index(subfiles)**

Returns an index that enables faster searching of *subfiles* using the *index_search* function. The returned index does NOT get updated when making changes to *subfiles* after the function is called.

**index_search(index, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, file_name='')**

Similar to the *search* function, but uses the index created by *build_index* for faster searching.

**read_file_name(subfile)**

Reads the file name of *subfile* for supported file types. Returns the name of the file if the file's type is supported, otherwise returns an empty sting.

### Dictionaries
Structure of dictionaries created by this script:

#### package (dict)
Dictionary containing *header* and *subfiles*

-----

#### header (dict)

**'major version':** int

Equal to 1.

**'minor version':** int

Equal to 1.

**'major user version'**: int

Equal to 0.

**'minor user version':** int

Equal to 0.

**'flags':** int

Not known.

**'created date':** int

**'modified date':** int

**'index major version':** int

Equal to 7.

**'index entry count':** int

The number of entries in the file.

**'index location':** int

The location of the file index.

**'index size':** int

The length of the index.

**'hole index entry count':** int

The number of holes in the file.

**'hole index location':** int

The location of the holes index in the file.

**'hole index size':** int

The length of the holes index.

**'index minor version':** int

The index version, between 0 and 2.

**'remainder':** bytes

What remains of the header.

-----

#### subfiles (list of dicts)
Usually called *entries*. Each element in this list contains the following:

**'type':** int

Entry type.

**'group':** int

Entry group.

**'instance':** int

Entry instance.

**'resource':** int

Entry resource, only exists if the *index minor version* of the *header* is 2.

**'content':** BytesIO

File-like object stored in memory containing the entry itself.

**'compressed':** bool

Indicates whether the entry is compressed or not.

## Resources
General information on DBPF (Package) files (A little dated): https://modthesims.info/wiki.php?title=DBPF

Useful image showing the game's file format: https://simswiki.info/images/e/e8/DBPF_File_Format_v1.1.png

Information on the various file types found in the package file's entries (A little dated): https://modthesims.info/wiki.php?title=List_of_Sims_2_Formats_by_Name

Information on the compression used by the game's files: https://modthesims.info/wiki.php?title=DBPF_Compression

Original code for the library I used for the compression and decompression code: www.moreawesomethanyou.com/smf/index.php/topic,8279.0.html

Notepad++ with the HEX-Editor plugin was useful for viewing the game's files: https://notepad-plus-plus.org/

SimPE also has a hex viewer, but it only shows you uncompressed entries: https://modthesims.info/showthread.php?t=630456

I used this tool to compare my edited files to the original files: https://github.com/Shelwien/cmp/