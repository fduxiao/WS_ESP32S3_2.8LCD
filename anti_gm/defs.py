from machine import *
from .st7796 import ST7796I80

sd = SDCard(cs=Pin(42), mosi=Pin(41), sck=Pin(40), miso=Pin(39), slot=2)

gps_en = Pin(2, Pin.OUT)
gps_uart = UART(1, baudrate=9600, tx=-1, rx=1)

light = ADC(Pin(4))
half_bat = ADC(Pin(5))


display = ST7796I80(
    res=7,
    cs=10,
    blk=6,
    dc=9,
    wr=46,
    data=[3, 20, 19, 8, 18, 17, 16, 15],
)

i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)

scr_int = Pin(13)
scr_cres = Pin(14)
i2c_en = Pin(21, Pin.OUT)
