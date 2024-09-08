from machine import *
import i8080
from . import st7796

i8080.clean_all()

sd = SDCard(cs=Pin(42), mosi=Pin(41), sck=Pin(40), miso=Pin(39), slot=2)

gps_uart = UART(1, baudrate=9600, tx=2, rx=1)
gps_en = Pin(2, Pin.OUT, value=0)

light = ADC(Pin(4))
half_bat = ADC(Pin(5))

# Some weird problem for D+, D-. See https://github.com/micropython/micropython/issues/11315.
# PWM(Pin(19)).deinit()
# PWM(Pin(20)).deinit()

scr_width = 320
scr_height = 480


display = st7796.ST7796I80(
    rst=7, blk=6,
    cs=10, dc=9, wr=46,
    data=[3, 20, 19, 8, 18, 17, 16, 15],
    width=scr_width, height=scr_height,
    dx=scr_width, dy=scr_height, rotation=180
)

display.clear(0xffff)
display.fill(0xffff)
display.text("hello world", 0, 0, 0x0000)
display.update()
display.display_on()

i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)

scr_int = Pin(13)
scr_cres = Pin(14)
i2c_en = Pin(21, Pin.OUT, value=0)
