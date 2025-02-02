#ifdef MICROPY_HW_BOARD_NAME
#undef MICROPY_HW_BOARD_NAME
#endif

#define MICROPY_HW_BOARD_NAME               "WS_ESP32S3_2.8LCD (esp32s3 spiram octal)"

#define MICROPY_HW_MCU_NAME                 "ESP32S3"

#define MICROPY_PY_MACHINE_DAC              (0)

// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (1)

#define MICROPY_HW_I2C0_SCL                 (3)
#define MICROPY_HW_I2C0_SDA                 (1)
