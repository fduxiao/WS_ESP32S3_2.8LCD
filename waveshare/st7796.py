from machine import Pin, PWM
from micropython import const
from time import sleep
import struct
from framebuf import FrameBuffer, RGB565


class ST7796(FrameBuffer):
    NOP = const(0x00)  # No-op
    SWRESET = const(0x01)  # Software reset
    RDDID = const(0x04)  # Read display ID info
    RDDST = const(0x09)  # Read display status
    GAMMASET = const(0x26)  # Gamma set

    SLPIN = const(0x10)  # Enter sleep mode
    SLPOUT = const(0x11)  # Exit sleep mode
    PTLON = const(0x12)  # Partial mode on
    NORON = const(0x13)  # Normal display mode on

    RDMODE = const(0x0A)  # Read display power mode
    RDMADCTL = const(0x0B)  # Read display MADCTL
    RDPIXFMT = const(0x0C)  # Read display pixel format
    RDIMGFMT = const(0x0D)  # Read display image format
    RDSELFDIAG = const(0x0F)  # Read display self-diagnostic

    INVOFF = const(0x20)  # Display inversion off
    INVON = const(0x21)  # Display inversion on
    DISPLAY_OFF = const(0x28)  # Display off
    DISPLAY_ON = const(0x29)  # Display on
    SET_COLUMN = const(0x2A)  # Column address set
    SET_PAGE = const(0x2B)  # Page address set
    WRITE_RAM = const(0x2C)  # Memory write
    READ_RAM = const(0x2E)  # Memory read

    PTLAR = const(0x30)  # Partial area
    VSCRDEF = const(0x33)  # Vertical scrolling definition
    MADCTL = const(0x36)  # Memory access control
    VSCRSADD = const(0x37)  # Vertical scrolling start address
    PIXFMT = const(0x3A)  # COLMOD: Pixel format set

    ST7796_MAD_MY   = const(0x80)
    ST7796_MAD_MX   = const(0x40)
    ST7796_MAD_MV   = const(0x20)
    ST7796_MAD_ML   = const(0x10)
    ST7796_MAD_BGR  = const(0x08)
    ST7796_MAD_MH   = const(0x04)
    ST7796_MAD_RGB  = const(0x00)
    ST7796_INVOFF   = const(0x20)
    ST7796_INVON    = const(0x21)

    WRITE_DISPLAY_BRIGHTNESS = const(0x51)  # Brightness hardware dependent!
    READ_DISPLAY_BRIGHTNESS = const(0x52)
    WRITE_CTRL_DISPLAY = const(0x53)

    READ_CTRL_DISPLAY = const(0x54)
    WRITE_CABC = const(0x55)  # Write Content Adaptive Brightness Control
    READ_CABC = const(0x56)  # Read Content Adaptive Brightness Control
    WRITE_CABC_MINIMUM = const(0x5E)  # Write CABC Minimum Brightness
    READ_CABC_MINIMUM = const(0x5F)  # Read CABC Minimum Brightness

    FRMCTR1 = const(0xB1)  # Frame rate control (In normal mode/full colors)
    FRMCTR2 = const(0xB2)  # Frame rate control (In idle mode/8 colors)
    FRMCTR3 = const(0xB3)  # Frame rate control (In partial mode/full colors)
    INVCTR = const(0xB4)  # Display inversion control
    DFUNCTR = const(0xB6)  # Display function control

    PWCTR1 = const(0xC0)  # Power control 1
    PWCTR2 = const(0xC1)  # Power control 2
    PWCTR3 = const(0xC2)  # Power control 3
    PWCTRA = const(0xCB)  # Power control A
    PWCTRB = const(0xCF)  # Power control B

    VMCTR1 = const(0xC5)  # VCOM control 1
    VMCOFF = const(0xC6)  # VCOM control 1
    VMCTR2 = const(0xC7)  # VCOM control 2
    RDID1 = const(0xDA)  # Read ID 1
    RDID2 = const(0xDB)  # Read ID 2
    RDID3 = const(0xDC)  # Read ID 3
    RDID4 = const(0xD3)  # const(0xDD)  # Read ID 4
    GMCTRP1 = const(0xE0)  # Positive gamma correction
    GMCTRN1 = const(0xE1)  # Negative gamma correction
    DTCA = const(0xE8)  # Driver timing control A
    DTCB = const(0xEA)  # Driver timing control B
    POSC = const(0xED)  # Power on sequence control
    ENABLE3G = const(0xF2)  # Enable 3 gamma control
    PUMPRC = const(0xF7)  # Pump ratio control

    ST7796_MADCTL_MY   = 0x80
    ST7796_MADCTL_MX   = 0x40
    ST7796_MADCTL_MV   = 0x20
    ST7796_MADCTL_ML   = 0x10
    ST7796_MADCTL_RGB  = 0x00
    ST7796_MADCTL_BGR  = 0x08
    ST7796_MADCTL_MH   = 0x04

    ROTATE = {
        0: 0x88,
        90: 0xE8,
        180: 0x48,
        270: 0x28
    }
    def __init__(self, rst, cs, dc, blk, width, height, rotation=180, offset_x=0, offset_y=0, dx=0, dy=0) -> None:
        self.rst = Pin(rst, Pin.OUT, value=1)
        if cs:
            self.cs = Pin(cs, Pin.OUT, value=1)
        if dc:
            self.dc = Pin(dc, Pin.OUT, value=0)
        self.blk_pwm = PWM(Pin(blk), duty=1023, freq=800)
        self.blk_value = 0
        self.width = width
        self.height = height

        if rotation not in self.ROTATE:
            raise RuntimeError('Rotation must be 0, 90, 180 or 270.')
        else:
            self.rotation = rotation
            self.rotation_cmd_param = self.ROTATE[rotation]

        # use the builtin framebuffer
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.dx = dx
        self.dy = dy

        size = dx * dy * 2  # rgb565
        self.buf = bytearray(size)
        super().__init__(self.buf, dx, dy, RGB565)

    def hard_reset(self):
        self.rst(0)
        sleep(.1)
        self.rst(1)
        sleep(.2)

    def soft_reset(self):
        self.write_cmd(self.SWRESET)
        sleep(.1)

    def sleep_out(self):
        self.write_cmd(self.SLPOUT)
        sleep(.120)

    def reset(self):
        self.hard_reset()
        self.soft_reset()
        self.sleep_out()

    def init(self):
        self.write_cmd(0xF0, 0xC3)
        self.write_cmd(0xF0, 0x96)
        self.write_cmd(self.MADCTL, self.rotation_cmd_param)

        self.write_cmd(self.PIXFMT, 0x05)
        # self.write_cmd(self.INVCTR, 0x01)
        # self.write_cmd(self.DFUNCTR, 0x80, 0x02, 0x3B)
        self.write_cmd(0xE8,
                       0x40, 0x82, 0x07, 0x18,
                       0x27, 0x0A, 0xB6, 0x33)

        self.write_cmd(self.VMCTR1, 0x27)
        self.write_cmd(self.PWCTR3, 0xA7)

        self.write_cmd(self.GMCTRP1,
                       0xF0, 0x01, 0x06, 0x0F,
                       0x12, 0x1D, 0x36, 0x54,
                       0x44, 0x0C, 0x18, 0x16,
                       0x13, 0x15)
        self.write_cmd(self.GMCTRN1,
                       0xF0, 0x01, 0x05, 0x0A,
                       0x0b, 0x07, 0x32, 0x44,
                       0x44, 0x0C, 0x18, 0x17,
                       0x13, 0x16)
        sleep(.1)
        self.write_cmd(0xF0, 0x3C)
        self.write_cmd(0xF0, 0x69)
        sleep(.1)

    def write_mem(self, data):
        self.write_color(self.WRITE_RAM, data)

    def block(self, x0, y0, x1, y1, data=None):
        self.write_cmd(self.SET_COLUMN, *struct.pack(">HH", x0, x1))
        self.write_cmd(self.SET_PAGE, *struct.pack(">HH", y0, y1))

        if data is None:
            data = bytearray()
        self.write_mem(data)

    def update(self):
        x0 = self.offset_x
        y0 = self.offset_y
        x1 = x0 + self.dx - 1
        y1 = y0 + self.dy - 1
        self.block(x0, y0, x1, y1, self.buf)

    def clear(self, color=0):
        w = self.width
        h = self.height

        if color:
            line = color.to_bytes(2, 'big') * (w * 8)
        else:
            line = bytearray(w * 16)
        for y in range(0, h, 8):
            self.block(0, y, w - 1, y + 7, line)

    def display_off(self):
        self.write_cmd(self.DISPLAY_OFF)

    def display_on(self):
        self.write_cmd(self.DISPLAY_ON)

    def deinit(self):
        self.blk_pwm.deinit()

    # overload the following for different peripherals
    def write_cmd(self, cmd, *args):
        pass

    def write_data(self, data):
        pass

    def write_color(self, cmd, color):
        self.write_cmd(cmd)
        self.write_data(color)

    def blk(self, value=None):
        if value is None:
            return self.blk_value
        self.blk_value = value
        duty_u16 = int(65535 * value)
        self.blk_pwm.duty_u16(duty_u16)


def split_data(data, step):
    len_data = len(data)
    mv = memoryview(data)
    start = 0
    while start < len_data:
        yield mv[start:start+step]
        start += step


class ST7796PY(ST7796):
    def __init__(self, rst, cs, dc, blk, wr, data,
                 width=320, height=480, rotation=0, offset_x=0, offset_y=0, dx=0, dy=0) -> None:

        self.wr = Pin(wr, Pin.OUT, value=1)
        self.data = [Pin(i, Pin.OUT) for i in data]
        super().__init__(rst=rst, cs=cs, dc=dc, blk=blk,
                         width=width, height=height, rotation=rotation,
                         offset_x=offset_x, offset_y=offset_y, dx=dx, dy=dy)

    def write_byte(self, dat):
        self.cs(0)
        self.wr(0)
        for i in range(8):
            pin = self.data[i]
            if dat & 0x01:
                pin(1)
            else:
                pin(0)
            dat >>= 1
        self.wr(1)
        self.cs(1)

    def write_cmd(self, cmd, *args):
        self.dc(0)
        self.write_byte(cmd)
        if args:
            self.write_data(bytearray(args))

    def write_data(self, data):
        self.dc(1)
        for b in data:
            self.write_byte(b)
