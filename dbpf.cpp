/*
 * Version 20070601.
 *
 * This file (with the exception of some parts adapted from zlib) is
 * Copyright 2007 Ben Rudiak-Gould. Anyone may use it under the terms of
 * the GNU General Public License, version 2 or (at your option) any
 * later version. This code comes with NO WARRANTY. Make backups!
 */

#include <string.h>  // for memcpy and memset
#include <stdlib.h>

//#include <assert.h>
#define assert(expr) do{}while(0)

// datatype assumptions: 8-bit bytes; sizeof(int) >= 4
typedef unsigned char byte;
struct word { byte lo,hi; };
struct dword { word lo,hi; };

#ifdef _X86_   // little-endian and no alignment restrictions
  static inline unsigned get(const word& w)     { return *(const unsigned short*)&w; }
  static inline unsigned get(const dword& dw)   { return *(const unsigned*)&dw; }
  static inline void put(word& w, unsigned x)   { *(unsigned short*)&w = x; }
  static inline void put(dword& dw, unsigned x) { *(unsigned*)&dw = x; }
#else
  static inline unsigned get(const word& w)     { return w.lo + w.hi * 256; }
  static inline unsigned get(const dword& dw)   { return get(dw.lo) + get(dw.hi) * 65536; }
  static inline void put(word& w, unsigned x)   { w.lo = x; w.hi = x >> 8; }
  static inline void put(dword& dw, unsigned x) { put(dw.lo, x); put(dw.hi, x >> 16); }
#endif

struct word3be { byte hi,mid,lo; };

static inline unsigned get(const word3be& w3)   { return w3.hi * 65536 + w3.mid * 256 + w3.lo; }
static inline void put(word3be& w3, unsigned x) { w3.hi = x >> 16; w3.mid = x >> 8; w3.lo = x; }

// Note that mynew and mydelete don't call the constructor or destructor (we don't have any)
template<class T>
static inline
T* mynew(int n)
{
    int size = n * sizeof(T);
    size += !size;  // don't depend on behavior of malloc(0)
    return (T*)malloc(size);
}

static inline
void mydelete(void* p) { if (p) free(p); }

extern "C" {
    bool decompress(const byte* src, int compressed_size, byte* dst, int uncompressed_size, bool truncate);
    byte* compress(const byte* src, const byte* srcend, byte* dst, byte* dstend, bool pad);
    int try_compress(const byte* src, int srclen, byte* dst);
}

static const int MAX_FILE_SIZE = 0x40000000;

/********************** low-level compression routines **********************/

struct dbpf_compressed_file_header  // 9 bytes
{
    dword compressed_size;
    word compression_id;       // DBPF_COMPRESSION_QFS
    word3be uncompressed_size;
};

#define DBPF_COMPRESSION_QFS (0xFB10)

bool decompress(const byte* src, int compressed_size, byte* dst, int uncompressed_size, bool truncate)
{
    const byte* src_end = src + compressed_size;
    byte* dst_end = dst + uncompressed_size;
    byte* dst_start = dst;

    if (compressed_size < (int)sizeof(dbpf_compressed_file_header) + 1)
        return false;
    const dbpf_compressed_file_header* hdr = (const dbpf_compressed_file_header*)src;

    if (get(hdr->compression_id) != DBPF_COMPRESSION_QFS)
        return false;

    int hdr_c_size = get(hdr->compressed_size), hdr_uc_size = get(hdr->uncompressed_size);
    if (truncate) {
        if (hdr_c_size < compressed_size || hdr_uc_size < uncompressed_size)
            return false;
    } else {
        if (hdr_c_size != compressed_size || hdr_uc_size != uncompressed_size)
            return false;
    }

    src += sizeof(dbpf_compressed_file_header);

    unsigned b0;
    do {
        int lit, copy, offset;
        b0 = *src++;
        if (b0 < 0x80) {
            if (src == src_end) return false;
            unsigned b1 = *src++;
            lit = b0 & 0x03;                        // 0..3
            copy = ((b0 & 0x1C) >> 2) + 3;          // 3..10
            offset = ((b0 & 0x60) << 3) + b1 + 1;   // 1..1024
        } else if (b0 < 0xC0) {
            if (src+2 > src_end) return false;
            unsigned b1 = *src++;
            unsigned b2 = *src++;
            lit = (b1 & 0xC0) >> 6;                 // 0..3
            copy = (b0 & 0x3F) + 4;                 // 4..67
            offset = ((b1 & 0x3F) << 8) + b2 + 1;   // 1..16384
        } else if (b0 < 0xE0) {
            if (src+3 > src_end) return false;
            unsigned b1 = *src++;
            unsigned b2 = *src++;
            unsigned b3 = *src++;
            lit = b0 & 0x03;                        // 0..3
            copy = ((b0 & 0x0C) << 6) + b3 + 5;     // 5..1028
            offset = ((b0 & 0x10) << 12) + (b1 << 8) + b2 + 1;  // 1..131072
        } else if (b0 < 0xFC) {
            lit = (b0 - 0xDF) * 4;                  // 4..112
            copy = 0;
            offset = 0;
        } else {
            lit = b0 - 0xFC;
            copy = 0;
            offset = 0;
        }
        if (src + lit > src_end || dst + lit + copy > dst_end) {
            if (!truncate)
                return false;
            if (lit > dst_end - dst)
                lit = dst_end - dst;
            if (copy > dst_end - dst - lit)
                copy = dst_end - dst - lit;
            if (src + lit > src_end)
                return false;
        }
        if (lit) {
            memcpy(dst, src, lit);
            dst += lit; src += lit;
        }
        if (copy) {
            if (offset > dst - dst_start)
                return false;
            if (offset == 1) {
                memset(dst, dst[-1], copy);
                dst += copy;
            } else {
                do {
                    *dst = *(dst-offset);
                    ++dst;
                } while (--copy);
            }
        }
    } while (src < src_end && dst < dst_end);

    if (truncate) {
        return (dst == dst_end);
    } else {
        while (src < src_end && *src == 0xFC)
            ++src;
        return (src == src_end && dst == dst_end);
    }
}

/*
 * Try to compress the data and return the result in a buffer (which the
 * caller must delete). If it's uncompressable, return NULL.
 */
 
int try_compress(const byte* src, int srclen, byte* dst)
{
    // There are only 3 byte for the uncompressed size in the header,
    // so I guess we can only compress files larger than 16MB...
    if (srclen < 14 || srclen >= 16777216) return 0;

    // We only want the compressed output if it's smaller than the
    // uncompressed.
    //dst = mynew<byte>(srclen-1);
    //if (!dst) return 0;

    byte* dstend = compress(src, src+srclen, dst, dst+srclen-1, false);
    if (dstend) {
        //int dstlen = dstend - dst;
        return dstend - dst;
    } else {
        //int dstlen = 0;
        //mydelete(dst);
        return 0;
    }
}

#define MAX_MATCH 1028
#define MIN_MATCH 3

#define MIN_LOOKAHEAD (MAX_MATCH+MIN_MATCH+1)

// corresponds to zlib compression level 9
#define GOOD_LENGTH 32
#define MAX_LAZY    258
#define NICE_LENGTH 258
#define MAX_CHAIN   4096

#define HASH_BITS 16
#define HASH_SIZE 65536
#define HASH_MASK 65535
#define HASH_SHIFT 6

#define W_SIZE 131072
#define MAX_DIST W_SIZE
#define W_MASK (W_SIZE-1)

class Hash
{
private:
    unsigned hash;
    int *head, *prev;
public:
    Hash() {
        hash = 0;
        head = mynew<int>(HASH_SIZE);
        for (int i=0; i<HASH_SIZE; ++i)
            head[i] = -1;
        prev = mynew<int>(W_SIZE);
    }
    ~Hash() {
        mydelete(head);
        mydelete(prev);
    }

    int getprev(unsigned pos) const { return prev[pos & W_MASK]; }

    void update(unsigned c) {
        hash = ((hash << HASH_SHIFT) ^ c) & HASH_MASK;
    }

    int insert(unsigned pos) {
        int match_head = prev[pos & W_MASK] = head[hash];
        head[hash] = pos;
        return match_head;
    }
};

class CompressedOutput
{
private:

    byte* dstpos;
    byte* dstend;
    const byte* src;
    unsigned srcpos;

public:

    CompressedOutput(const byte* src_, byte* dst, byte* dstend_) {
        dstpos = dst; dstend = dstend_; src = src_;
        srcpos = 0;
    }

    byte* get_end() { return dstpos; }

    bool emit(unsigned from_pos, unsigned to_pos, unsigned count)
    {
        if (count)
            assert(memcmp(src + from_pos, src + to_pos, count) == 0);

        unsigned lit = to_pos - srcpos;

        while (lit >= 4) {
            unsigned amt = lit>>2;
            if (amt > 28) amt = 28;
            if (dstpos + amt*4 >= dstend) return false;
            *dstpos++ = 0xE0 + amt - 1;
            memcpy(dstpos, src + srcpos, amt*4);
            dstpos += amt*4;
            srcpos += amt*4;
            lit -= amt*4;
        }

        unsigned offset = to_pos - from_pos - 1;

        if (count == 0) {
            if (dstpos+1+lit > dstend) return false;
            *dstpos++ = 0xFC + lit;
        } else if (offset < 1024 && 3 <= count && count <= 10) {
            if (dstpos+2+lit > dstend) return false;
            *dstpos++ = ((offset >> 3) & 0x60) + ((count-3) * 4) + lit;
            *dstpos++ = offset;
        } else if (offset < 16384 && 4 <= count && count <= 67) {
            if (dstpos+3+lit > dstend) return false;
            *dstpos++ = 0x80 + (count-4);
            *dstpos++ = lit * 0x40 + (offset >> 8);
            *dstpos++ = offset;
        } else /* if (offset < 131072 && 5 <= count && count <= 1028) */ {
            if (dstpos+4+lit > dstend) return false;
            *dstpos++ = 0xC0 + ((offset >> 12) & 0x10) + (((count-5) >> 6) & 0x0C) + lit;
            *dstpos++ = offset >> 8;
            *dstpos++ = offset;
            *dstpos++ = (count-5);
        }

        for (; lit; --lit) *dstpos++ = src[srcpos++];
        srcpos += count;

        return true;
    }
};

/*
 * The following two functions (longest_match and compress) are loosely
 * adapted from zlib 1.2.3's deflate.c, and are probably still covered by
 * the zlib license, which carries this notice:
 */
/* zlib.h -- interface of the 'zlib' general purpose compression library
  version 1.2.3, July 18th, 2005

  Copyright (C) 1995-2005 Jean-loup Gailly and Mark Adler

  This software is provided 'as-is', without any express or implied
  warranty.  In no event will the authors be held liable for any damages
  arising from the use of this software.

  Permission is granted to anyone to use this software for any purpose,
  including commercial applications, and to alter it and redistribute it
  freely, subject to the following restrictions:

  1. The origin of this software must not be misrepresented; you must not
     claim that you wrote the original software. If you use this software
     in a product, an acknowledgment in the product documentation would be
     appreciated but is not required.
  2. Altered source versions must be plainly marked as such, and must not be
     misrepresented as being the original software.
  3. This notice may not be removed or altered from any source distribution.

  Jean-loup Gailly        Mark Adler
  jloup@gzip.org          madler@alumni.caltech.edu


  The data format used by the zlib library is described by RFCs (Request for
  Comments) 1950 to 1952 in the files http://www.ietf.org/rfc/rfc1950.txt
  (zlib format), rfc1951.txt (deflate format) and rfc1952.txt (gzip format).
*/

static inline
unsigned longest_match(
    int cur_match,
    const Hash& hash,
    const byte* const src,
    const byte* const srcend,
    unsigned const pos,
    unsigned const remaining,
    unsigned const prev_length,
    unsigned* pmatch_start)
{
    unsigned chain_length = MAX_CHAIN;         /* max hash chain length */
    int best_len = prev_length;                /* best match length so far */
    int nice_match = NICE_LENGTH;              /* stop if match long enough */
    int limit = pos > MAX_DIST ? pos - MAX_DIST + 1 : 0;
    /* Stop when cur_match becomes < limit. */

    const byte* const scan = src+pos;

    /* This is important to avoid reading past the end of the memory block */
    if (best_len >= (int)remaining)
        return remaining;

    const int max_match = (remaining < MAX_MATCH) ? remaining : MAX_MATCH;
    byte scan_end1  = scan[best_len-1];
    byte scan_end   = scan[best_len];

    /* Do not waste too much time if we already have a good match: */
    if (prev_length >= GOOD_LENGTH) {
        chain_length >>= 2;
    }
    /* Do not look for matches beyond the end of the input. This is necessary
     * to make deflate deterministic.
     */
    if ((unsigned)nice_match > remaining) nice_match = remaining;

    do {
        assert(cur_match < pos);
        const byte* match = src + cur_match;

        /* Skip to next match if the match length cannot increase
         * or if the match length is less than 2.
         */
        if (match[best_len]   != scan_end  ||
            match[best_len-1] != scan_end1 ||
            match[0]          != scan[0]   ||
            match[1]          != scan[1])      continue;

        /* It is not necessary to compare scan[2] and match[2] since they
         * are always equal when the other bytes match, given that
         * the hash keys are equal and that HASH_BITS >= 8.
         */
        assert(scan[2] == match[2]);

        int len = 2;
        do { ++len; } while (len < max_match && scan[len] == match[len]);

        if (len > best_len) {
            *pmatch_start = cur_match;
            best_len = len;
            if (len >= nice_match || scan+len >= srcend) break;
            scan_end1  = scan[best_len-1];
            scan_end   = scan[best_len];
        }
    } while ((cur_match = hash.getprev(cur_match)) >= limit
             && --chain_length > 0);

    return best_len;
}

/* Returns the end of the compressed data if successful, or NULL if we overran the output buffer */

byte* compress(const byte* src, const byte* srcend, byte* dst, byte* dstend, bool pad)
{
    unsigned match_start = 0;
    unsigned match_length = MIN_MATCH-1;           /* length of best match */
    bool match_available = false;         /* set if previous match exists */

    unsigned pos = 0, remaining = srcend - src;

    if (remaining >= 16777216) return 0;

    CompressedOutput compressed_output(src, dst+sizeof(dbpf_compressed_file_header), dstend);

    Hash hash;
    hash.update(src[0]);
    hash.update(src[1]);

    while (remaining) {

        unsigned prev_length = match_length;
        unsigned prev_match = match_start;
        match_length = MIN_MATCH-1;

        int hash_head = -1;

        if (remaining >= MIN_MATCH) {
            hash.update(src[pos + MIN_MATCH-1]);
            hash_head = hash.insert(pos);
        }

        if (hash_head >= 0 && prev_length < MAX_LAZY && pos - hash_head <= MAX_DIST) {

            match_length = longest_match (hash_head, hash, src, srcend, pos, remaining, prev_length, &match_start);

            /* If we can't encode it, drop it. */
            if ((match_length <= 3 && pos - match_start > 1024) || (match_length <= 4 && pos - match_start > 16384))
                match_length = MIN_MATCH-1;
        }
        /* If there was a match at the previous step and the current
         * match is not better, output the previous match:
         */
        if (prev_length >= MIN_MATCH && match_length <= prev_length) {

            if (!compressed_output.emit(prev_match, pos-1, prev_length))
                return 0;

            /* Insert in hash table all strings up to the end of the match.
             * pos-1 and pos are already inserted. If there is not
             * enough lookahead, the last two strings are not inserted in
             * the hash table.
             */
            remaining -= prev_length-1;
            prev_length -= 2;
            do {
                ++pos;
                if (src+pos <= srcend-MIN_MATCH) {
                    hash.update(src[pos + MIN_MATCH-1]);
                    hash.insert(pos);
                }
            } while (--prev_length != 0);
            match_available = false;
            match_length = MIN_MATCH-1;
            ++pos;

        } else  {
            match_available = true;
            ++pos;
            --remaining;
        }
    }
    assert(pos == srcend - src);
    if (!compressed_output.emit(pos, pos, 0))
        return 0;

    byte* dstsize = compressed_output.get_end();
    if (pad && dstsize < dstend) {
        memset(dstsize, 0xFC, dstend-dstsize);
        dstsize = dstend;
    }

    dbpf_compressed_file_header* hdr = (dbpf_compressed_file_header*)dst;
    put(hdr->compressed_size, dstsize - dst);
    put(hdr->compression_id, DBPF_COMPRESSION_QFS);
    put(hdr->uncompressed_size, srcend-src);

    return dstsize;
}
