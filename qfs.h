/*
 * Library interface for compressing and decompressing assets
 * using the RefPack compression algorithm.
 *
 * This file (with the exception of some parts adapted from zlib) is
 * Copyright 2007 Ben Rudiak-Gould. Anyone may use it under the terms of
 * the GNU General Public License, version 2 or (at your option) any
 * later version. This code comes with NO WARRANTY. Make backups!
 */

#ifndef QFS_H
#define QFS_H

typedef unsigned char byte;

extern "C" {
	
/*
 * Decompresses src and stores the output in dst.
 * Returns a boolean indicating if the decompression was successful.
 */
bool qfs_decompress(const byte* src, int srclen, byte* dst, int dstlen);

/*
 * Compresses src and stores the output in dst.
 * Returns the length of the compressed output if successful, otherwise returns 0.
 */
int qfs_compress(const byte* src, int srclen, byte* dst, int dstlen);

}

#endif