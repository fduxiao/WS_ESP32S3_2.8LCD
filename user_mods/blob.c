// Include MicroPython API.
#include "py/binary.h"
#include "py/runtime.h"
#include "py/obj.h"
#include "py/objarray.h"

#include "blob.h"


void* malloc_dma(size_t size, bool spiram) {

    // allocate heap memory
    uint32_t caps = MALLOC_CAP_8BIT | MALLOC_CAP_DMA;
    if(spiram) {
        caps |= MALLOC_CAP_SPIRAM;
    } else {
        caps |= MALLOC_CAP_INTERNAL;
    }
    void* data = heap_caps_malloc(size, caps);
    return data;
}


// Make a blob directly.
mp_obj_t new_dma_blob(size_t size, bool spiram) {
    void* data = malloc_dma(size, spiram);
    if(data == NULL) {
        return mp_const_none;
    }
    Blob_obj_t* self = mp_obj_malloc(Blob_obj_t, &type_Blob);
    self->data = data;
    self->size = size;
    return MP_OBJ_FROM_PTR(self);
}

// Constructor of Blob class.
static mp_obj_t Blob_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    Blob_obj_t* self = mp_obj_malloc(Blob_obj_t, type);
    self->size = 0;
    self->data = NULL;
    return MP_OBJ_FROM_PTR(self);;
}


// Allocate DMA-compatible memory.
static mp_obj_t Blob_malloc_dma(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_self, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
        { MP_QSTR_size, MP_ARG_REQUIRED | MP_ARG_INT, {.u_int = -1} },
        { MP_QSTR_spiram, MP_ARG_KW_ONLY | MP_ARG_BOOL, {.u_bool = false} },
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    Blob_obj_t *self = MP_OBJ_TO_PTR(args[0].u_obj);
    if(self->data != NULL) {
        mp_raise_ValueError("free blob before use it");
        return mp_const_none;
    }
    mp_int_t size = args[1].u_int;
    bool spiram = args[2].u_bool;

    if(size <= 0) {
        mp_raise_ValueError("size should be positive");
        return mp_const_none;
    }
    
    size_t usize = (size_t)size;
    void* data = malloc_dma(size, spiram);
    if(data == NULL) {
        mp_raise_OSError(CANNOT_ALLOCATE_MEMORY);
        return mp_const_none;
    }
    self->data = data;
    self->size = usize;

    return MP_OBJ_FROM_PTR(self);
}

static MP_DEFINE_CONST_FUN_OBJ_KW(Blob_malloc_dma_obj, 1, Blob_malloc_dma);

static mp_obj_t Blob_free(mp_obj_t self_in) {
    Blob_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if(self->data != NULL) {
        heap_caps_free(self->data);
        self->data = NULL;
        self->size = 0;
    }
    return mp_const_none;
}

static MP_DEFINE_CONST_FUN_OBJ_1(Blob_free_obj, Blob_free);


static mp_obj_t Blob_memoryview(mp_obj_t self_in) {
    Blob_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if(self->data == NULL) {
        return mp_const_none;
    }

    size_t typecode = BYTEARRAY_TYPECODE | MP_OBJ_ARRAY_TYPECODE_FLAG_RW;
    return mp_obj_new_memoryview(typecode, self->size, self->data);
}

static MP_DEFINE_CONST_FUN_OBJ_1(Blob_memoryview_obj, Blob_memoryview);

static mp_obj_t Blob_bytearray(mp_obj_t self_in) {
    Blob_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if(self->data == NULL) {
        return mp_const_none;
    }
    return mp_obj_new_bytearray_by_ref(self->size, self->data);
}
static MP_DEFINE_CONST_FUN_OBJ_1(Blob_bytearray_obj, Blob_bytearray);

// Collection of all static methods and locals of the new type.
static const mp_rom_map_elem_t Blob_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_malloc_dma), MP_ROM_PTR(&Blob_malloc_dma_obj) },
    { MP_ROM_QSTR(MP_QSTR_free), MP_ROM_PTR(&Blob_free_obj) },
    { MP_ROM_QSTR(MP_QSTR_memoryview), MP_ROM_PTR(&Blob_memoryview_obj) },
    { MP_ROM_QSTR(MP_QSTR_mv), MP_ROM_PTR(&Blob_memoryview_obj) },
    { MP_ROM_QSTR(MP_QSTR_bytearray), MP_ROM_PTR(&Blob_bytearray_obj) },
    { MP_ROM_QSTR(MP_QSTR_bs), MP_ROM_PTR(&Blob_bytearray_obj) },
};
static MP_DEFINE_CONST_DICT(Blob_locals_dict, Blob_locals_dict_table);


// This defines the type_Blob object.
MP_DEFINE_CONST_OBJ_TYPE(
    type_Blob,
    MP_QSTR_Blob,
    MP_TYPE_FLAG_NONE,
    make_new, Blob_make_new,
    locals_dict, &Blob_locals_dict
);


// Define the module attributes.
static const mp_rom_map_elem_t blob_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_blob) },
    { MP_ROM_QSTR(MP_QSTR_Blob), MP_ROM_PTR(&type_Blob) },
};

static MP_DEFINE_CONST_DICT(blob_globals, blob_globals_table);


// Define module object.
const mp_obj_module_t blob_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&blob_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_blob, blob_module);
