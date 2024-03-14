# Purpose

1- To make it easier to access and read the game's data.

2- To enable quick script editing of the game's files.

# Getting Started

**Requirements:** 

1- Windows 7 or higher

2- Python 3.2 or higher

3- [StructIO](https://github.com/lingeringwillx/StructIO)

4- Mingw-w64 (Only if you want to recompile the C library)

**Installation:**

Download the build and place it in a folder named 'dbpf'. Outside the folder, create a python file and write `import dbpf` to import the library.

# Objects

## Package

Creates an object resembling the structure of a *.package* file.

### Attributes

**header** (Header): Contains the [header](#Header)

**entries** (list\[Entry]): Contains instances of [Entry](#Entry).

**file_path** (str): The path of the file that was used to create the Package object.

### Methods

**Package()**

Creates a Package object containing the data required to make an empty package file.

**Package.unpack(file_path, decompress=False, read_names=False)**

Static method. Reads a package file from the provided *file_path* and returns a *Package* object containing its data. If *decompress* is True, then all of the package's entries will be decompressed. If *read_names* is set to True, then the method will try to get all the names of the package's entries. Note that reading the names of the entries is slow.

**pack_into(file_path, compress=False)**

Converts the Package object into a package file and writes it to a file with the provided *file_path*. If *compress* is True, then the function will try to compress all of the package's entries.

**copy()**

Creates a copy of the package and returns it.

## Header

### Attributes

**major_version** (int): Equal to 1.

**minor_version** (int): Between 0 and 2.

**major_user_version** (int): Equal to 0.

**minor_user_version** (int): Equal to 0.

**flags** (int): Not known.

**created_date** (int)

**modified_date** (int)

**index_major_version** (int): Equal to 7.

**index_entry_count** (int): The number of entries in the file.

**index_location** (int): The location of the file's index.

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

Inherits from [StructIO](https://github.com/lingeringwillx/StructIO).

### Attributes

**type** (int): Entry type.

**group** (int): Entry group.

**instance** (int): Entry instance.

**resource** (int): Entry resource.

**compressed** (bool): Indicates whether the entry is compressed or not.

**name** (str): Contains the name of the entry for supported entry types. Keep in mind that changing this value will not change the actual name in the entry's content. To apply the new name to the entry, use the *write_name* function.

### Methods

**Entry(type_id, group_id, instance_id, resource_id=0, name='', content=b'', compressed=False)**

Creates an entry containing the provided arguments.

**copy()**

Creates a copy of the entry and returns it.

**compress()**

Compresses the content of the entry. If the content of the entry is already compressed, then nothing happens. Returns a reference to the entry.

**decompress()**

Decompresses the content of the entry. If the content of the entry is already decompressed, then nothing happens. Raises a *CompressionError* if decompression fails. Returns a reference to the entry.

**read_name()**

Reads the name of the entry from it's content and writes it to *name*. Returns the name of the entry if the entry's type is supported, otherwise returns an empty string.

# Functions

**partial_decompress(entry, size=-1)**

Decompresses *entry* up to *size*. If *size* is not specified, then the whole entry will be decompressed. Returns a StructIO object containing the decompressed bytes. Unlike the *decompress* function, this function does not overwrite the contents of *entry*.

**search(entries, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, entry_name='', get_first=False)**

Searches the a list of entries for the desired type, group, instance, or resource, returns a list of the entries matching the criteria. if any of the arguments is set equal to -1 then the the function will ignore that specific argument. If *entry_name* is specified, then the function will check if the names of supported file types contain *entry_name*. If *get_first* is set to *True*, then the function will directly return a list containing the first entry that it finds.

**build_index(entries)**

Returns an index that enables faster searching of *entries* using the *index_search* function. The returned index does NOT get updated when making changes to *entries* after the function is called.

**index_search(entries, index, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, entry_name='')**

Similar to the *search* function, but uses the index created by *build_index* for faster searching. Useful when you need to search a large package mutiple times.

# Resources
General information on DBPF (Package) files (A little dated): https://modthesims.info/wiki.php?title=DBPF

Useful image showing the game's entry format: https://simswiki.info/images/e/e8/DBPF_File_Format_v1.1.png

Information on the various entry types found in the package file's entries (A little dated): https://modthesims.info/wiki.php?title=List_of_Sims_2_Formats_by_Name

Information on the compression used by the game's files: https://modthesims.info/wiki.php?title=DBPF_Compression

Original code for the library I used for the compression and decompression code: www.moreawesomethanyou.com/smf/index.php/topic,8279.0.html

Notepad++ with the HEX-Editor plugin was useful for viewing the game's files: https://notepad-plus-plus.org/

SimPE also has a hex viewer, but it only shows you uncompressed entries: https://modthesims.info/showthread.php?t=630456

I used this tool to compare my edited files to the original files: https://github.com/Shelwien/cmp/
