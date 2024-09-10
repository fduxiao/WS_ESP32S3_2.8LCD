import lvgl as lv
from uasyncio import create_task, Loop, sleep
import lv_utils
from .lv_driver import LVDispDriver, LVTouchInput
from ..board import Board


class UIApp:
    def __init__(self, board: Board) -> None:
        self.board: Board = board
        self.width = board.scr_width
        self.height = board.scr_height

    def init(self):
        # hardware init
        self.board.init()

        # lvgl
        if not lv.is_initialized():
            lv.init()

        # prepare the event loop
        if not lv_utils.event_loop.is_running():
            self.lv_event_loop = lv_utils.event_loop(asynchronous=True)

        self.lv_display_driver = LVDispDriver(self.width, self.height, display=self.board.display)
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

    def setup_tasks(self):
        create_task(self.heart_beat())

    def run_forever(self):
        return Loop.run_forever()

    def main(self):
        self.init()
        self.setup_tasks()
        self.main_scr()
        self.run_forever()

    def main_scr(self):
        # the example3 from lvgl
        scr1 = lv.obj()
        scr2 = lv.obj()
        lv.scr_load(scr1)

        # scr1
        button1 = lv.btn(scr1)
        button1.align(lv.ALIGN.TOP_RIGHT, -5, 5)
        label = lv.label(button1)
        label.set_text(">")

        button1.add_event(lambda e: lv.scr_load(scr2), lv.EVENT.CLICKED, None)

        # keyboard + textarea
        ta = lv.textarea(scr1)
        ta.set_width(320)
        ta.set_height(70)
        ta.align(lv.ALIGN.CENTER, 0, -70)
        ta.set_text("")

        kb = lv.keyboard(scr1)
        kb.set_textarea(ta)

        # scr2
        button2 = lv.btn(scr2)
        button2.align(lv.ALIGN.TOP_LEFT, 5, 5)
        label2 = lv.label(button2)
        label2.set_text("<")

        button2.add_event(lambda e: lv.scr_load(scr1), lv.EVENT.CLICKED, None)

        slider = lv.slider(scr2)
        slider.set_width(150)
        slider.align(lv.ALIGN.TOP_MID, 0, 15)

        led1 = lv.led(scr2)
        led1.align(lv.ALIGN.CENTER, 0, 0)
        led1.set_brightness(slider.get_value() * 2)
        led1.set_size(20, 20)

        slider.add_event(lambda e: led1.set_brightness(slider.get_value() * 2), lv.EVENT.VALUE_CHANGED, None)
