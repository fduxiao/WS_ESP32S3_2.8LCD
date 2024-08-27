set(IDF_TARGET esp32s3)

set(LV_CFLAGS -DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1)

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    boards/sdkconfig.usb
    boards/sdkconfig.ble
    boards/sdkconfig.240mhz
    boards/sdkconfig.spiram_sx
    boards/sdkconfig.spiram_oct
    boards/AntiGM/sdkconfig.board
)

list(APPEND IDF_COMPONENTS
    esp_lcd
)

list(APPEND MICROPY_DEF_BOARD
    MICROPY_HW_BOARD_NAME="AntiGM"
)


# extra modules
set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
