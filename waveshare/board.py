from machine import *
from .st7796 import ST7796
from .cst328 import CST328
from .qmi8658 import QMI8658


class Board:
    key0: Pin
    i2c_tp: I2C

    lcd_blk: int
    key_bat: Pin
    bat_control: Pin
    bat_one_third: ADC

    i2c: I2C
    rtc_init: Pin
    imu_init1: Pin
    imu_init2: Pin

    sd: SDCard
    sd_d2: Pin
    sd_d1: Pin

    i2s_rate: int
    i2s_bits: int
    i2s_buf_size: int
    i2s: I2S

    pin_rxd: Pin
    pin_txd: Pin

    touch: CST328
    display: ST7796
    imu: QMI8658

    def init_screen_and_touch(self):
        self.touch.init()

    def init(self):
        self.blk(0)

        self.init_screen_and_touch()

        self.display.reset()
        self.display.init()
        self.display.clear(0xffff)

        # framebuf
        self.display.fill(0xffff)
        loading = "Loading..."
        width = len(loading) * 8
        height = 8
        self.display.text(loading, (self.display.dx - width) // 2, (self.display.dy - height) // 2, 0x0000)
        self.display.update()

        # turn on the display
        self.display.display_on()
        self.blk(1)

        # i2c devices
        self.imu.init()

    def deinit(self):
        self.display.deinit()

    def blk(self, value=None):
        return self.display.blk(value)

    def read_imu(self):
        return self.imu.read_accelerometer(), self.imu.read_gyproscope()
