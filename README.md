## Purpose
1- To make it easier to access and read the game's data.

2- To enable quick script editing of the game's files .

## Documentation
## Functions:
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

Reads a package file and returns a dictionary containing its data. For information on the dictionary, check the [next section](#dictionaries)

**create_package()**

Creates a dictionary containing the data necessary to create an empty package file.

**write_package(file, package)**

Converts the dictionary *package* into a package file and writes it to *file*.

**search(subfiles, ntype=-1, ngroup=-1, ninstance=-1, ninstance2=-1, get_first=False)**

searches the package's files for the desired type, group, instance, or high instance, returns a list of the indexes of the files matching the criteria. if any of the arguments is set equal to -1 then the the function will ignore that specific argument. If *get_first* is set to *True*, then the function will directly return a list containing the first index that it finds.

**compress(subfile)**

returns a copy of *subfile* with it's content compressed. If the content of *subfile* is already compressed, then it returns an identical copy. 

**decompress(subfile)**

returns a copy of *subfile* with it's content decompressed. If the content of *subfile* is already decompressed, then it returns an identical copy. 

**print_TGI(subfile)**

displays the type, group, and instance of a *subfile*

## Dictionaries
Structure of dictionaries created by this script:

### Package (dict)
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

**'remainder':** 32 bytes

What remains of the header.

-----

#### Subfiles (list of dicts)
Each element in this list contains the following:

**'type':** int

Entry type.

**'group':** int

Entry group.

**'instance':** int

Entry instance.

**'instance2':** int

Entry second instance, only exists if the entry has a second instance (if the index minor version is 2).

**'content':** BytesIO

File-like object stored in memory containing the entry itself.

**'compressed':** bool

Indicates whether the entry is compressed or not.
