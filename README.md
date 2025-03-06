## Purpose

1- To make it easier to access and read the game's data.

2- To enable quick script editing of the game's files.

## Getting Started

**Requirements:** 

1- [StructIO](https://github.com/lingeringwillx/StructIO)

2- MinGW (Only if you want to recompile the C library)

**Installation:**

Download the build and rename the extracted folder to 'dbpf'. Outside the folder, create a python file and write `import dbpf` to import the library.

## Objects

### Package

Creates an object resembling the structure of a *.package* file.

#### Attributes

**header** (Header): Contains the [header](#Header)

**entries** (list\[Entry]): Contains instances of [Entry](#Entry).

**path** (str): The path of the file that was used to create the Package object.

#### Methods

**Package()**

Creates a Package object containing the data required to make an empty package file.

**Package.unpack(path, decompress=False, read_names=False)**

Static method. Reads a package file from the provided *path* and returns a *Package* object containing its data. If *decompress* is True, then all of the package's entries will be decompressed. If *read_names* is set to True, then the method will try to get all the names of the package's entries. Note that reading the names of the entries is slow.

**pack_into(path, compress=False)**

Converts the Package object into a package file and writes it to a file with the provided *path*. If *compress* is True, then the function will try to compress all of the package's entries.

**copy()**

Creates a copy of the package and returns it.

### Entry

Inherits from [StructIO](https://github.com/lingeringwillx/StructIO).

#### Attributes

**type** (int): Entry type.

**group** (int): Entry group.

**instance** (int): Entry instance.

**resource** (int): Entry resource.

**compressed** (bool): Indicates whether the entry is compressed or not.

**name** (str): Contains the name of the entry for supported entry types. Keep in mind that changing this value will not change the actual name in the entry's content.

#### Methods

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

## Functions

**search(entries, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, entry_name='')**

Searches the a list of entries for the desired type, group, instance, or resource, returns a list of the entries matching the criteria. if any of the arguments is set equal to -1 then the the function will ignore that specific argument. If *entry_name* is specified, then the function will check if the names of supported file types contain *entry_name*. Searching the names requires unpacking the package with the *read_names* argument set to True.

## Resources
General information on DBPF (Package) files (A little dated): https://modthesims.info/wiki.php?title=DBPF

Useful image showing the structure of a package file: https://simswiki.info/images/e/e8/DBPF_File_Format_v1.1.png

Information on the various entry types found in the game's package files (A little dated): https://modthesims.info/wiki.php?title=List_of_Sims_2_Formats_by_Name

Information on the compression algorithm used in the game's files: https://modthesims.info/wiki.php?title=DBPF_Compression

Original code for the library I used for the compression and decompression: http://www.moreawesomethanyou.com/smf/index.php/topic,8279.0.html

Notepad++ with the HEX-Editor plugin was useful for viewing the game's files: https://notepad-plus-plus.org/

SimPE also has a hex viewer, but it only shows you uncompressed entries: https://modthesims.info/showthread.php?t=630456

I used this tool to compare my edited files to the original files: https://github.com/Shelwien/cmp/
