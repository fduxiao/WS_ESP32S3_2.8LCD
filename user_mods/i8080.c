// Include MicroPython API.
#include "py/runtime.h"

#include "blob.h"
// ESP LCD API
#include "esp_lcd_types.h"
#include "esp_lcd_panel_io.h"

#ifndef LCD_CLK_SRC_DEFAULT
#define LCD_CLK_SRC_DEFAULT LCD_CLK_SRC_PLL160M
#endif

// This structure represents the i8080 bus class I80
typedef struct _I80_obj_t {
    // All objects start with the base.
    mp_obj_base_t base;
    int width;
    int height;
    esp_lcd_i80_bus_handle_t i80_bus;
    esp_lcd_panel_io_handle_t io_handle;
} I80_obj_t;


// Constructor of I80 class.
static mp_obj_t I80_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    // Allocates the new object and sets the type.
    I80_obj_t *self = mp_obj_malloc(I80_obj_t, type);
    self->i80_bus = NULL;
    self->io_handle = NULL;

    // The make_new function always returns self.
    return MP_OBJ_FROM_PTR(self);
}


// Initialize the i80 bus.
static mp_obj_t I80_init(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    // we specify the dc, wr, data as keyword arguments. 
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_self, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
        { MP_QSTR_width, MP_ARG_KW_ONLY | MP_ARG_REQUIRED | MP_ARG_INT, {.u_int = -1} },
        { MP_QSTR_height, MP_ARG_KW_ONLY | MP_ARG_REQUIRED | MP_ARG_INT, {.u_int = -1} },
        { MP_QSTR_cs, MP_ARG_KW_ONLY | MP_ARG_REQUIRED | MP_ARG_INT, {.u_int = -1} },
        { MP_QSTR_dc, MP_ARG_KW_ONLY | MP_ARG_REQUIRED | MP_ARG_INT, {.u_int = -1} },
        { MP_QSTR_wr, MP_ARG_KW_ONLY | MP_ARG_REQUIRED | MP_ARG_INT, {.u_int = -1} },
        { MP_QSTR_data, MP_ARG_KW_ONLY | MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL } },
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    I80_obj_t *self = MP_OBJ_TO_PTR(args[0].u_obj);
    mp_int_t width = args[1].u_int;
    mp_int_t height = args[2].u_int;
    mp_int_t cs = args[3].u_int;
    mp_int_t dc = args[4].u_int;
    mp_int_t wr = args[5].u_int;
    mp_obj_t data = args[6].u_obj;

    self->width = width;
    self->height = height;

    // setup basic config
    esp_lcd_i80_bus_config_t bus_config = {
        .clk_src = LCD_CLK_SRC_DEFAULT,
        .dc_gpio_num = (int)dc,
        .wr_gpio_num = (int)wr,
        .bus_width = 0,
        .max_transfer_bytes = width * height * sizeof(uint16_t) / 10,
        // .dma_burst_size = EXAMPLE_DMA_BURST_SIZE,  // unavailable in v4.4
    };

    // parse data gpio nums

    mp_obj_iter_buf_t iter_buf;
    mp_obj_t item, iterable = mp_getiter(data, &iter_buf);
    while ((item = mp_iternext(iterable)) != MP_OBJ_STOP_ITERATION) {
        bus_config.data_gpio_nums[bus_config.bus_width] = mp_obj_get_int(item);
        bus_config.bus_width += 1;
    }

    // create the i80 bus
    esp_err_t err = esp_lcd_new_i80_bus(&bus_config, &self->i80_bus);
    if(err != ESP_OK) {
        mp_raise_OSError(err);
        return mp_const_none;
    }

    // setup the panel io
    esp_lcd_panel_io_i80_config_t io_config = {
        .cs_gpio_num = cs,
        .pclk_hz = 20000000,  // 20MHz
        .trans_queue_depth = 10,
        .dc_levels = {
            .dc_idle_level = 0,
            .dc_cmd_level = 0,
            .dc_dummy_level = 0,
            .dc_data_level = 1,
        },
        .lcd_cmd_bits = 8,
        .lcd_param_bits = 8,
    };
    err = esp_lcd_new_panel_io_i80(self->i80_bus, &io_config, &self->io_handle);
    if(err != ESP_OK) {
        mp_raise_OSError(err);
        return mp_const_none;
    }

    return mp_const_none;
}

static MP_DEFINE_CONST_FUN_OBJ_KW(I80_init_obj, 1, I80_init);

static mp_obj_t I80_deinit(mp_obj_t self_in) {
    I80_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if(self->io_handle != NULL) {
        esp_err_t err = esp_lcd_panel_io_del(self->io_handle);
        if(err != ESP_OK) {
            mp_raise_OSError(err);
            return mp_const_none;
        }
        self->io_handle = NULL;
    }

    if(self->i80_bus != NULL) {
        esp_err_t err = esp_lcd_del_i80_bus(self->i80_bus);
        if(err != ESP_OK) {
            mp_raise_OSError(err);
            return mp_const_none;
        }
        self->i80_bus = NULL;
    }
    return mp_const_none;
}

static MP_DEFINE_CONST_FUN_OBJ_1(I80_deinit_obj, I80_deinit);


// Make an i80 compatible memory
static mp_obj_t I80_malloc_dma(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_self, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
        { MP_QSTR_size, MP_ARG_REQUIRED | MP_ARG_INT, {.u_int = -1} },
        { MP_QSTR_spiram, MP_ARG_KW_ONLY | MP_ARG_BOOL, {.u_bool = false} },
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    I80_obj_t *self = MP_OBJ_TO_PTR(args[0].u_obj);
    mp_int_t size = args[1].u_int;
    bool spiram = args[2].u_bool;

    if(size <= 0) {
        mp_raise_ValueError("size should be positive");
        return mp_const_none;
    }
    
    size_t usize = (size_t)size;

    (void)self;
    return new_dma_blob(usize, spiram);
}

static MP_DEFINE_CONST_FUN_OBJ_KW(I80_malloc_dma_obj, 1, I80_malloc_dma);

static mp_obj_t I80_write_cmd(mp_obj_t self_in, mp_obj_t cmd_in, mp_obj_t param) {
    I80_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_int_t cmd = mp_obj_get_int(cmd_in);
    // get memory buffer from data
    mp_buffer_info_t bufinfo;
    if(!mp_get_buffer(param, &bufinfo, MP_BUFFER_READ)) {
        mp_raise_TypeError("object with buffer protocol required for param");
        return mp_const_none;
    }
    esp_err_t err = esp_lcd_panel_io_tx_param(self->io_handle, cmd, bufinfo.buf, bufinfo.len);
    if(err != ESP_OK) {
        mp_raise_OSError(err);
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_3(I80_write_cmd_obj, I80_write_cmd);


static mp_obj_t I80_write_color(mp_obj_t self_in, mp_obj_t cmd_in, mp_obj_t param) {
    I80_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_int_t cmd = mp_obj_get_int(cmd_in);
    // get memory buffer from data
    mp_buffer_info_t bufinfo;
    if(!mp_get_buffer(param, &bufinfo, MP_BUFFER_READ)) {
        mp_raise_TypeError("object with buffer protocol required for param");
        return mp_const_none;
    }
    esp_err_t err = esp_lcd_panel_io_tx_color(self->io_handle, cmd, bufinfo.buf, bufinfo.len);
    if(err != ESP_OK) {
        mp_raise_OSError(err);
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_3(I80_write_color_obj, I80_write_color);


// Collection of all static methods and locals of the new type.
static const mp_rom_map_elem_t I80_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&I80_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&I80_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR_malloc_dma), MP_ROM_PTR(&I80_malloc_dma_obj) },
    { MP_ROM_QSTR(MP_QSTR_write_cmd), MP_ROM_PTR(&I80_write_cmd_obj) },
    { MP_ROM_QSTR(MP_QSTR_write_color), MP_ROM_PTR(&I80_write_color_obj) },
};
static MP_DEFINE_CONST_DICT(I80_locals_dict, I80_locals_dict_table);


// This defines the type(I80) object.
MP_DEFINE_CONST_OBJ_TYPE(
    type_I80,
    MP_QSTR_I8080,
    MP_TYPE_FLAG_NONE,
    make_new, I80_make_new,
    locals_dict, &I80_locals_dict
);


// Define the module attributes.
static const mp_rom_map_elem_t i8080_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_i8080) },
    { MP_ROM_QSTR(MP_QSTR_I8080), MP_ROM_PTR(&type_I80) },
};

static MP_DEFINE_CONST_DICT(i8080_globals, i8080_globals_table);


// Define module object.
const mp_obj_module_t i8080_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&i8080_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_i8080, i8080_module);
