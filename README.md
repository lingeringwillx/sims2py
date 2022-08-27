## Purpose
1- To make it easier to access and read the game's data.

2- To enable quick script editing of the game's files .

## Documentation
### Functions:
**read(file, numbytes, endian='little')**

Reads *numbytes* from *file* and converts it into an integer. The endian can be specified with the *endian* argument.

**write(file, num, numbytes, endian='little')**

Converts *num* into a bytes object with length *numbytes* and endian *endian*, then writes it into *file*.

**read_str(file)**

Reads from *file* until it reaches a null termination and returns a string.

**write_str(file, string)**

Writes *string* into *file*

**get_size(file)**

Returns the size/length of *file*

**copy(object)**

Returns a copy of *object*. Identical to copy.deepcopy from the standard library.

**read_package(file)**

Reads a package file and returns a dictionary containing its data. For information on the dictionary, check the [dictionaries](#dictionaries) section.

**create_package()**

Creates a dictionary containing the data necessary to create an empty package file.

**write_package(file, package)**

Converts the dictionary *package* into a package file and writes it to *file*.

**search(subfiles, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1, get_first=False)**

searches the package's files for the desired type, group, instance, or resource, returns a list of the indices of the subfiles matching the criteria. if any of the arguments is set equal to -1 then the the function will ignore that specific argument. If *get_first* is set to *True*, then the function will directly return a list containing the first index that it finds.

**compress(subfile)**

returns a copy of *subfile* with it's content compressed. If the content of *subfile* is already compressed, then it returns an identical copy. 

**decompress(subfile)**

returns a copy of *subfile* with it's content decompressed. If the content of *subfile* is already decompressed, then it returns an identical copy. 

**print_TGI(subfile)**

displays the type, group, and instance of a *subfile*.

**build_index(subfiles)**

returns an index that enables faster searching of *subfiles* using the *index_search* function. The returned index does **NOT** get updated when making changes to *subfiles* after the function is called.

**index_search(index, type_id=-1, group_id=-1, instance_id=-1, resource_id=-1)**

similar to the *search* function, but uses the index created by *build_index* for faster searching.

### Dictionaries
Structure of dictionaries created by this script:

#### Package (dict)
Dictionary containing *Header* and *Subfiles*

-----

#### Header (dict)

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

#### Subfiles (list of dicts)
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

Information on the various file types found in the package file's entries (A little dated): https://modthesims.info/wiki.php?title=Category:InternalFormats

Information on the compression used by the game's files: https://modthesims.info/wiki.php?title=DBPF_Compression

Original code for the library I used for the compression and decompression code: www.moreawesomethanyou.com/smf/index.php/topic,8279.0.html

Notepad++ with the HEX-Editor plugin was useful for viewing the game's files: https://notepad-plus-plus.org/

SimPE also has a hex viewer, but it only shows you uncompressed entries: https://modthesims.info/showthread.php?t=630456

I used this tool to compare my edited files to the original files: https://github.com/Shelwien/cmp/
