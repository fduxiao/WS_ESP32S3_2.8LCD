from machine import *
import lvgl as lv
from asyncio import create_task, sleep
from waveshare import Board, ST7789SPI, CST328, UIApp, QMI8658, Page


class MyBoard(Board):
    key0 = Pin(0)
    i2c_tp = I2C(1, scl=Pin(3), sda=Pin(1), freq=400_000)
    touch = CST328(i2c_tp, addr=0x1A, int=Pin(4), rst=Pin(2, Pin.OUT, value=0))

    lcd_blk = 5
    key_bat = Pin(6)
    bat_control = Pin(7)
    bat_one_third = ADC(Pin(8))

    i2c = I2C(0, scl=Pin(10), sda=Pin(11), freq=400_000)
    rtc_init = Pin(9)
    imu_init1 = Pin(13)
    imu_init2 = Pin(12)
    imu = QMI8658(i2c)

    sd = SDCard(cs=Pin(21), mosi=Pin(17), sck=Pin(14), miso=Pin(16), slot=2)
    sd_d2 = Pin(15)
    sd_d1 = Pin(18)

    i2s_rate = 44100
    i2s_bits = 16
    i2s_buf_size = 40000
    i2s = I2S(0, sck=Pin(48),  # BCLK
              ws=Pin(38),  # LRCK
              sd=Pin(47),  # SDATA
              mode=I2S.TX, bits=i2s_bits, format=I2S.STEREO, rate=i2s_rate, ibuf=i2s_buf_size)  

    pin_txd = Pin(43)
    pin_rxd = Pin(44)

    scr_width = 240
    scr_height = 320
    display = ST7789SPI(rst=39, cs=42, dc=41, blk=lcd_blk,
                        spi=SPI(1, baudrate=20_000_000,  # polarity=0, phase=0, bits=8, firstbit=0,
                                sck=Pin(40), mosi=Pin(45), miso=Pin(46)),
                        width=scr_width, height=scr_height, dx=100, dy=100)


class HelloWorldPage(Page):
    def __init__(self, board):
        super().__init__(board)
        label = lv.label(self)
        label.align(lv.ALIGN.TOP_MID, 0, 100)
        label.set_text("Hello world")

        label = lv.label(self)
        label.align(lv.ALIGN.TOP_MID, 0, 200)
        self.label = label
        self.task = None
        self.t = 0

    def on_load(self):
        self.label.set_text("tick: ")
        return super().on_load()
    
    async def timer(self):
        while True:
            self.label.set_text(f"tick: {self.t}")
            self.t += 1
            self.t %= 3600
            await sleep(1)
    
    def on_activate(self):
        if self.task is not None:
            self.task.cancel()
        self.task = create_task(self.timer())
    
    def on_deactivate(self):
        if self.task is not None:
            self.task.cancel()
            self.task = None


class MyApp(UIApp):
    def setup_pages(self):
        self.add_page(HelloWorldPage)
        super().setup_pages()

    def main(self):
        print('customized main')
        return super().main()


board = MyBoard()
app = MyApp(board)
