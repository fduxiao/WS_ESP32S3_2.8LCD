from micropython import const
from collections import namedtuple
import struct
import time
from machine import Pin


REG_XY_RESOLUTION = 0xD1F8
REG_VERIFY_BOOT = 0xD1FC

REG_DEBUG_INFO = 0xD101
REG_SOFT_RESET = 0xD102
REG_DEEPSLEEP = 0xD105
REG_NORMAL_MODE = 0xD109

REG_TOUCH_FINGER1 = 0xD000
REG_TOUCH_NUM = 0xD005
REG_TOUCH_FINGER2 = 0xD007

TouchPos = namedtuple("TouchPos", ("id", "x", "y", "c", "pressed"))
TouchInfo = namedtuple("TouchInfo", ("num", "large", "points"))


def parse_pos(bs):
    data = struct.unpack('<BHHH', bs)
    return TouchPos(*data)


class CST328:
    def __init__(self, i2c, addr, int, rst) -> None:
        self.i2c = i2c
        self.addr = addr
        self.int = int
        self.rst = rst
        self.width = 0
        self.height = 0

    def hard_reset(self):
        self.rst(1)
        time.sleep(0.050)
        self.rst(0)
        time.sleep(0.010)
        self.rst(1)
        time.sleep(0.050)

        self.int.init(Pin.IN)

    def soft_reset(self):
        self.write_reg(REG_SOFT_RESET)
        time.sleep(0.10)

    def sleep(self):
        self.write_reg(REG_DEEPSLEEP)

    def init(self):
        self.hard_reset()
        self.soft_reset()

        # enter debug mode
        self.write_reg(REG_DEBUG_INFO)
        # read caca
        data = self.read_reg(REG_VERIFY_BOOT, 4)
        if data[2:5] != b"\xca\xca":
            raise RuntimeError("wrong verification", data[2:5])
        print('boot time: %x, %x' % (data[0], data[1]))
        data = self.read_reg(REG_XY_RESOLUTION, 4)
        x, y = struct.unpack('<HH', data)
        self.width = x
        self.height = y
        print(f"resolution: (x, y) = ({x}, {y})")
        self.write_reg(REG_NORMAL_MODE)

    def read_reg(self, reg, size=1):
        reg = struct.pack(">H", reg)
        self.i2c.writeto(self.addr, reg)
        return self.i2c.readfrom(self.addr, size)

    def write_reg(self, reg, data=None):
        bs = bytearray(2)
        reg = struct.pack_into(">H", bs, 0, reg)
        if isinstance(data, int):
            data = bytearray([data])
        if data is None:
            data = bytearray()
        bs.extend(data)
        return self.i2c.writeto(self.addr, bs)

    def irq(self, func):
        self.int.irq(func, Pin.IRQ_RISING)

    def read_one_finger(self, index):
        if index == 0:
            reg = REG_TOUCH_FINGER1
        else:
            reg = REG_TOUCH_FINGER2 + (index - 1) * 5
        data = self.read_reg(reg, 5)
        f_id = data[0] >> 4
        pressed = data[0] & 0x0f == 0x06
        b = data[3]
        x = data[1] << 4 | (b >> 4)
        y = data[2] << 4 | (b & 0x0F)
        c = data[4]
        return TouchPos(f_id, x, y, c, pressed)

    def read(self):
        num = self.read_reg(REG_TOUCH_NUM, 1)[0] & 0x0F
        if num == 0:
            return None
        points = [self.read_one_finger(0)]
        max_c = points[0].c
        for i in range(1, num):
            pos = self.read_one_finger(i)
            max_c = max(pos.c, max_c)
            points.append(pos)
        return TouchInfo(num, max_c, points)

    def set_debug_irq(self):
        def print_info(_):
            info = self.read()
            if info is None:
                return
            print(info)

        self.irq(print_info)
