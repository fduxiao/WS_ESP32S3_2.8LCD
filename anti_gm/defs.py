from machine import *

sd = SDCard(cs=Pin(42), mosi=Pin(41), sck=Pin(40), miso=Pin(39), slot=2)

gps_en = Pin(2, Pin.OUT)
gps_uart = UART(1, baudrate=9600, tx=-1, rx=1)

light = ADC(Pin(4))
half_bat = ADC(Pin(5))

scr_pwm = 6
scr_res = 7

scr_data = {
    'd0': 3,
    'd1': 20,
    'd2': 19,
    'd3': 8,
    'd4': 18,
    'd5': 17,
    'd6': 16,
    'd7': 15,
}

scr_wr = 46
scr_dc = 9
scr_cs = 10

i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)

scr_int = Pin(13)
scr_cres = Pin(14)
i2c_en = Pin(21, Pin.OUT)
