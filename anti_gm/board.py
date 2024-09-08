import time
from machine import *
from .st7796 import ST7796


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

    scr_int: Pin
    scr_cres: Pin
    i2c_en: Pin

    touch_addr = 0x14

    def init_screen_and_touch(self):
        self.scr_cres(0)
        time.sleep(0.010)
        self.scr_cres(1)
        time.sleep(0.010)

        self.scr_int.init(Pin.OUT, value=1)
        self.scr_cres(1)
        time.sleep(0.020)
        self.scr_cres(0)
        self.scr_int(0)
        time.sleep(0.020)
        # we first set int to 1 to select addr
        self.scr_int(self.touch_addr == 0x14)
        # wait for more than 5ms
        time.sleep(0.020)
        # then pull up rst
        self.scr_cres(1)
        time.sleep(0.020)
        # finally turn int into input
        self.scr_int.init(Pin.IN)

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
