#ifndef _MP_BLOB_HEADER
#define _MP_BLOB_HEADER

#include "py/obj.h"

#define CANNOT_ALLOCATE_MEMORY 12

// This structure represents some heap-allocated memory outside of gc
typedef struct _Blob_obj_t {
    // All objects start with the base.
    mp_obj_base_t base;
    size_t size;
    void* data;
} Blob_obj_t;

extern const mp_obj_type_t type_Blob;
mp_obj_t new_dma_blob(size_t size, bool spiram);

#endif
