from i8080 import I8080
from machine import Pin, PWM


class ST7796:
    pass


class ST7796I80(ST7796):
    def __init__(self, res, cs, blk, dc, wr, data, width=320, height=380, rotate=0) -> None:
        self.res = Pin(res, Pin.OUT)
        self.blk = PWM(Pin(blk), duty=1023, freq=800)
        self.i80_driver = I8080()
        self.i80_driver.init(cs=cs, dc=dc, wr=wr, data=data, width=width, height=height)
        self.rotate = 0

    def deinit(self):
        self.blk.deinit()
        self.i80_driver.deinit()
