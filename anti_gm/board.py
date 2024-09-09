import time
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
        self.i2c_en(1)
        self.init_screen_and_touch()

        self.display.reset()
        self.display.init()
        self.display.fill(0xffff)
        self.display.text("hello world", 0, 0, 0x0000)
        self.display.update()
        self.display.display_on()

    def deinit(self):
        self.display.deinit()
