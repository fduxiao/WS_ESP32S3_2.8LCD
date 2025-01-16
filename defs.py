from machine import *
from waveshare import Board, ST7796PY, GT911, UIApp


class MyBoard(Board):
    sd = SDCard(cs=Pin(42), mosi=Pin(41), sck=Pin(40), miso=Pin(39), slot=2)

    gps_uart = UART(1, baudrate=9600, tx=2, rx=1)
    gps_en = Pin(2, Pin.OUT, value=0)

    light_adc = ADC(Pin(4))
    half_bat_adc = ADC(Pin(5))

    scr_width = 320
    scr_height = 480

    display = ST7796PY(
        rst=7, blk=6,
        cs=10, dc=9, wr=46,
        data=[3, 20, 19, 8, 18, 17, 16, 15],
        width=scr_width, height=scr_height,
        dx=scr_width, dy=scr_height, rotation=180
    )

    i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)
    i2c_en = Pin(21, Pin.OUT, value=0)

    touch = GT911(i2c, addr=0x14, int=Pin(13), rst=Pin(14, Pin.OUT, value=0))


class MyApp(UIApp):
    def main(self):
        print('customized main')
        return super().main()


board = MyBoard()
app = MyApp(board)
