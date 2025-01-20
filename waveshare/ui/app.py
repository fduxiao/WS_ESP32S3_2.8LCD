import lvgl as lv
from uasyncio import create_task, Loop, sleep
import lv_utils
from .lv_driver import LVDispDriver, LVTouchInput
from ..board import Board


class UIApp:
    lv_disp_factor = 5

    def __init__(self, board: Board) -> None:
        self.board: Board = board
        self.width = board.scr_width
        self.height = board.scr_height
        self.pages = []
        self.imu_label = None

    def init(self):
        # hardware init
        self.board.init()

        # lvgl
        if not lv.is_initialized():
            lv.init()

        # prepare the event loop
        if not lv_utils.event_loop.is_running():
            self.lv_event_loop = lv_utils.event_loop(asynchronous=True)

        self.lv_display_driver = LVDispDriver(self.width, self.height, display=self.board.display,
                                              factor=self.lv_disp_factor)
        self.lv_indev_driver = LVTouchInput(touch=self.board.touch)

    def deinit(self):
        self.board.deinit()
        self.lv_display_driver.deinit()
        lv.deinit()

    async def heart_beat(self):
        i = 0
        while True:
            print(f'heart beat: {i}')
            await sleep(1)
            i += 1
            i %= 3600

    async def update_imu(self):
        while True:
            if self.imu_label is None:
                continue
            (ax, ay, az), (gx, gy, gz) = self.board.read_imu()
            self.imu_label.set_text(f"imu data: {ax:.1f}, {ay:.1f}, {az:.1f}")
            await sleep(0.1)

    def setup_tasks(self):
        create_task(self.heart_beat())
        create_task(self.update_imu())

    def run_forever(self):
        return Loop.run_forever()

    def main(self):
        self.init()
        self.main_scr()
        self.setup_tasks()
        self.run_forever()

    def add_page(self):
        scr = lv.obj()
        page_prev = None
        if len(self.pages) > 0:
            page_prev = self.pages[-1]
        if page_prev:
            btn_next = lv.button(page_prev)

            btn_next.align(lv.ALIGN.TOP_RIGHT, -5, 5)
            label = lv.label(btn_next)
            label.set_text(">")
            btn_next.add_event_cb(lambda e: lv.screen_load(scr), lv.EVENT.CLICKED, None)

            btn_prev = lv.button(scr)
            btn_prev.align(lv.ALIGN.TOP_LEFT, 5, 5)
            label2 = lv.label(btn_prev)
            label2.set_text("<")

            btn_prev.add_event_cb(lambda e: lv.screen_load(page_prev), lv.EVENT.CLICKED, None)
        else:
            lv.screen_load(scr)
        self.pages.append(scr)
        return scr

    def main_scr(self):
        # the example3 from lvgl
        scr1 = self.add_page()

        # keyboard + textarea
        ta = lv.textarea(scr1)
        ta.set_width(240)
        ta.set_height(70)
        ta.align(lv.ALIGN.CENTER, 0, -70)
        ta.set_text("")

        kb = lv.keyboard(scr1)
        kb.set_textarea(ta)

        scr2 = self.add_page()

        slider = lv.slider(scr2)
        slider.set_width(120)
        slider.align(lv.ALIGN.TOP_MID, 0, 15)

        led1 = lv.led(scr2)
        led1.align(lv.ALIGN.CENTER, 0, 0)
        led1.set_brightness(slider.get_value() * 2)
        led1.set_size(20, 20)

        slider.add_event_cb(lambda e: led1.set_brightness(slider.get_value() * 2), lv.EVENT.VALUE_CHANGED, None)

        slider2 = lv.slider(scr2)
        slider2.set_value(100, lv.ANIM.OFF)
        slider2.set_width(120)
        slider2.align(lv.ALIGN.TOP_MID, 0, 100)

        slider2.add_event_cb(lambda e: self.board.blk(0.2 + slider2.get_value() / 100 * 0.8), lv.EVENT.VALUE_CHANGED, None)

        scr3 = self.add_page()
        label = lv.label(scr3)
        label.align(lv.ALIGN.TOP_MID, 0, 100)
        label.set_text("imu data:")
        self.imu_label = label

        scr4 = self.add_page()
        btn = lv.button(scr4)
        btn.align(lv.ALIGN.TOP_MID, 0, 50)
        label = lv.label(btn)
        label.set_text("play sound")

        def play_music(e):
            from math import pi, sin
            time = 1
            freq = 440
            omega = 2 * pi * freq
            step = 1 / self.board.i2s_rate
            data = bytearray()
            amp = 1 << (self.board.i2s_bits - 1)
            amp /= 4
            for i in range(time * self.board.i2s_rate):
                value = amp * sin(step * i * omega)
                value = int(value)
                for _ in range(self.board.i2s_bits // 8):
                    data.append(value & 0xff)
                    value >>= 8
            self.board.i2s.write(data)
            print('play music')
        btn.add_event_cb(play_music, lv.EVENT.CLICKED, None)
