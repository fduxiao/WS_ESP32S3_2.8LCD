import time
from machine import *
from .st7796 import ST7796
from .gt911 import GT911
from .ui import LVDispDriver
import lvgl as lv


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

        lv.init()
        self.lv_display_driver = LVDispDriver(self.scr_width, self.scr_height, blit=self.lv_blit)
        btn = lv.btn(lv.scr_act())
        btn.align(lv.ALIGN.CENTER, 0, 0)
        btn.add_event(lambda e: print("touched", e), lv.EVENT.CLICKED, None)
        label = lv.label(btn)
        label.set_text("Hello World!")

    def deinit(self):
        self.display.deinit()
        self.lv_display_driver.deinit()
        lv.deinit()

    def lv_blit(self, area, color):
        x1 = area.x1
        x2 = area.x2
        y1 = area.y1
        y2 = area.y2

        self.display.block(x1, y1, x2, y2, color)
