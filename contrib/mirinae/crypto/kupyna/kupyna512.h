// Kupyna hash function implementation by sjinks
// https://github.com/sjinks/kupyna-c/

#ifndef KUPYNA512_H_
#define KUPYNA512_H_

#include <stdint.h>
#if defined(__SSE2__)
#include <emmintrin.h>
#elif defined(__SSE__)
#include <xmmintrin.h>
#elif defined(__MMX__)
#include <mmintrin.h>
#endif

union uint1024_t {
#if defined(__SSE2__)
    __m128i h[8];
#elif defined(__SSE__)
    __m128 h[8];
#elif defined(__MMX__)
    __m64 mq[16];
#endif
    uint64_t q[16];
    uint8_t b[128];
};

struct kupyna512_ctx_t {
    union uint1024_t h;
    union uint1024_t m;
    size_t pos;
    uint64_t total;
};

void kupyna512_init(struct kupyna512_ctx_t* ctx);
void kupyna512_update(struct kupyna512_ctx_t* ctx, const uint8_t* data, size_t len);
void kupyna512_update_aligned(struct kupyna512_ctx_t* ctx, const uint8_t* data, size_t len);
void kupyna512_final(struct kupyna512_ctx_t* ctx, uint8_t* hash);
void kupyna512_final2(struct kupyna512_ctx_t* ctx, uint8_t* hash, size_t bits);

void kupyna384_init(struct kupyna512_ctx_t* ctx);
void kupyna384_update(struct kupyna512_ctx_t* ctx, const uint8_t* data, size_t len);
void kupyna384_update_aligned(struct kupyna512_ctx_t* ctx, const uint8_t* data, size_t len);
void kupyna384_final(struct kupyna512_ctx_t* ctx, uint8_t* hash);

#endif /* KUPYNA512_H_ */
