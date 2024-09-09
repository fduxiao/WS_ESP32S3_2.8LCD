from micropython import const
from collections import namedtuple
import struct
import time
from machine import Pin


GT911_REG_CMD = const(0x8040)
GT911_CMD_RST = const(2)
GT911_CMD_READ = const(0)
GT911_CMD_OFF = const(5)

GT911_REG_PROD = const(0x8140)
GT911_REG_TOUCH_NUM = const(0x814E)
GT911_REG_TOUCH_PT1 = const(0x814F)
GT911_PT_STEP = const(8)
GT911_PT_NUM = const(5)


TouchPos = namedtuple("TouchPos", ("id", "x", "y", "c"))
TouchInfo = namedtuple("TouchInfo", ("num", "large", "points"))


def parse_pos(bs):
    data = struct.unpack('<BHHH', bs)
    return TouchPos(*data)


class GT911:
    def __init__(self, i2c, addr, int, rst) -> None:
        self.i2c = i2c
        self.addr = addr
        self.int = int
        self.rst = rst

    def hard_reset(self):
        self.rst(0)
        time.sleep(0.010)
        self.rst(1)
        time.sleep(0.010)

        self.int.init(Pin.OUT, value=1)
        self.rst(1)
        time.sleep(0.020)
        self.rst(0)
        self.int(0)
        time.sleep(0.020)
        # we first set int to 1 to select addr
        self.int(self.addr == 0x14)
        # wait for more than 5ms
        time.sleep(0.020)
        # then pull up rst
        self.rst(1)
        time.sleep(0.020)
        # finally turn int into input
        self.int.init(Pin.IN)

    def soft_reset(self):
        self.write_reg(GT911_REG_CMD, GT911_CMD_RST)
        time.sleep(0.10)
        self.write_reg(GT911_REG_CMD, GT911_CMD_READ)

    def off(self):
        self.write_reg(GT911_REG_CMD, GT911_CMD_OFF)

    def read_prod_id(self):
        return self.read_reg(GT911_REG_PROD, 4)

    def init(self):
        self.hard_reset()
        self.soft_reset()
        prod_id = self.read_prod_id()
        if prod_id != b'911\x00':
            raise RuntimeError("unknown device", prod_id)

    def read_reg(self, reg, size=1):
        reg = struct.pack(">H", reg)
        self.i2c.writeto(self.addr, reg)
        return self.i2c.readfrom(self.addr, size)

    def write_reg(self, reg, data):
        bs = bytearray(2)
        reg = struct.pack_into(">H", bs, 0, reg)
        if isinstance(data, int):
            data = bytearray([data])
        bs.extend(data)
        return self.i2c.writeto(self.addr, bs)

    def irq(self, func):
        self.int.irq(func, Pin.IRQ_RISING)

    def read_period(self):
        status = self.read_reg(GT911_REG_TOUCH_NUM, 1)[0]
        if not (status & 0b1000_0000):
            return None
        large = status & 0b0100_0000
        num = status & 0b0000_1111
        points = []
        for i in range(GT911_PT_NUM):
            bs = self.read_reg(GT911_REG_TOUCH_PT1 + i * GT911_PT_STEP, 7)
            points.append(parse_pos(bs))
        self.write_reg(GT911_REG_TOUCH_NUM, 0)
        return TouchInfo(num, large, points)

    def set_debug_irq(self):
        def print_info(_):
            info = self.read_period()
            if info is None:
                return
            print(info)

        self.irq(print_info)
