#ifndef _DBPF_H_
#define _DBPF_H_

/*
 * Library interface for reading and writing DBPF package files from
 * The Sims 2. Not currently compatible with SimCity 4.
 * Version 20070601.
 *
 * This file is Copyright 2007 Ben Rudiak-Gould. Anyone may use it
 * under the terms of the GNU General Public License, version 2 or
 * (at your option) any later version. This code comes with
 * NO WARRANTY. Make backups!
 */


#ifdef __cplusplus
extern "C" {
#endif


struct DBPF;


struct dbpf_entry
{
    unsigned type_id, group_id;
    unsigned instance_id, instance_id_2;
    int size;  // decompressed

    char write_disposition;  // only for entries passed to dbpf_write; see enum below

    char compressed_in_file;  // 0 for no, 1 for yes
    int offset_in_file, size_in_file;
};

enum {  // write dispositions

    dbpf_write_keep_existing = 0,  // keep existing file; all *_in_file fields must be valid

    dbpf_write_uncompressed = 1,   // don't try to compress

    dbpf_write_compressed = 2,     // try to compress; will write uncompressed if the data is incompressible

    dbpf_write_compressed_raw = 3, // the supplied data is already compressed (with header);
                                   // size must be uncompressed size and size_in_file must be compressed size

    dbpf_write_skip = 4,           // ignore this entry (supplied for convenience)
};


#define DBPF_EMPTY_ARCHIVE_LENGTH 96

/*
 * Retrieves the contents of an empty archive into the buffer, which must
 * hold DBPF_EMPTY_ARCHIVE_LENGTH bytes.
 */
void dbpf_create(unsigned char* buf);


/*
 * Opens a DBPF file. Uses read/write callbacks so that it's not bound to
 * some particular file access model; I hate libraries that force you to
 * use stdio.
 *
 * The read callback should succeed, returning a nonnegative number, only
 * if the entire read request is satisfied; no partial reads. It should
 * fail otherwise, returning a negative number and setting the error string.
 *
 * The write callback should succeed except in unusual circumstances (like
 * disk full). Writes past the end of the file should succeed, increasing
 * the file length. A length of zero is a special case: it should truncate
 * the file at the given position. The write callback can be NULL if you're
 * not planning on doing any writing.
 *
 * The close callback is called by dbpf_open if the open fails; otherwise
 * it's called by dbpf_close.
 *
 * dbpf_open returns NULL on failure. If the failure was caused by a
 * negative return from a callback, *error will contain whatever the
 * callback put in it; otherwise it will contain an English error message.
 */
DBPF* dbpf_open(
void* ctx,     // opaque file pointer
    int (*read)(void* ctx, int start, int length, void* buf, const char** error),
    int (*write)(void* ctx, int start, int length, const void* buf, const char** error),
    int (*close)(void* ctx),
    const char** error);


/*
 * Calls the close callback and then frees the DBPF structure. Returns
 * whatever value the close callback returns. dbpf_close(0) is legal and
 * does nothing.
 */
int dbpf_close(DBPF* dbpf);


/*
 * Returns the number of file entries in an opened archive.
 */
int dbpf_get_entry_count(const DBPF* dbpf);

/*
 * Returns an array of the file entries in an opened archive.
 */
const struct dbpf_entry* dbpf_get_entries(const DBPF* dbpf);


/*
 * Reads a file (decompressing it if necessary). Returns -1 on error.
 * *error is set as for dbpf_open.
 */
int dbpf_read(DBPF* dbpf, int entry_index, unsigned char* buf, const char** error);


/*
 * Quickly reads the first 64 bytes of a file, which often (not always)
 * contains the file name. Fails if the file is shorter than 64 bytes.
 */
int dbpf_read_64bytes(DBPF* dbpf, int entry_index, unsigned char* buf, const char** error);


/*
 * Updates a file in place, without changing any indexing information.
 * This might be useful for modifying data while the game is running.
 * The new data must be the same length as the old.
 *
 * NOTE RETURN VALUE! It returns 1 for success, -1 for a write error, and
 * 0 if the old data was compressed and the new data doesn't compress well
 * enough to fit. In the case of a 0 return, the file is left unmodified.
 * In the case of a -1 return, the file may be corrupt.
 */
int dbpf_update_in_place(DBPF* dbpf, int entry_index, const unsigned char* buf, const char** error);


/*
 * Rewrites the file based on the new index you provide. This is a safe
 * update: if it fails (negative return), the archive is still valid with
 * all its old contents intact. This means that it can't overwrite
 * anything, so the file size may double if you rewrite the whole thing.
 * This is fine for development. For distribution you should recompress
 * the whole file anyway (see dbpf-recompress.cpp).
 *
 * If the function succeeds, the old index is invalid and you should call
 * dbpf_get_entry_count and dbpf_get_entries again.
 *
 * This uses a callback for the data, rather than a pointer in dbpf_entry,
 * so that it doesn't all need to be in memory at once. The callback can
 * reuse the same buffer for each call. The callback will only be called
 * for index entries that don't specify dbpf_write_keep_existing. The
 * callback can fail (returning NULL) which causes the function to fail.
 *
 * Do not include an entry of type 0xE86B1EEF (compressed file directory).
 * The function will fail if you do.
 */
int dbpf_write(
    DBPF* dbpf,
    const struct dbpf_entry* new_entries,
    int new_entry_count,
    void* ctx,
    const unsigned char* (*get_data)(void* ctx, int entry_index, const char** error),
    const char** error);


/*
 * A convenience function for comparing the type, group, and instance of
 * two dbpf_entries. Returns positive, negative or zero a la strcmp().
 */
int dbpf_compare_entries(const dbpf_entry* left, const dbpf_entry* right);


#ifdef __cplusplus
}
#endif

#endif
