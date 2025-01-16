from machine import *
from .st7796 import ST7796
from .gt911 import GT911


class Board:
    sd: SDCard

    gps_uart: UART
    gps_en: Pin

    light: ADC
    half_bat: ADC

    scr_width = 320
    scr_height = 480

    display: ST7796

    i2c: I2C

    i2c_en: Pin

    touch: GT911

    def init_screen_and_touch(self):
        self.touch.init()

    def init(self):
        # turn on i2c
        self.i2c_en(1)
        # screen
        self.init_screen_and_touch()

        self.display.reset()
        self.display.init()
        self.display.fill(0xffff)
        loading = "Loading..."
        width = len(loading) * 8
        height = 8
        self.display.text(loading, (self.scr_width - width) // 2, (self.scr_height - height) // 2, 0x0000)
        self.display.update()
        self.display.display_on()

    def deinit(self):
        self.display.deinit()

    def blk(self, value=None):
        return self.display.blk(value)
