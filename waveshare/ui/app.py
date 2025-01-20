import lvgl as lv
from uasyncio import create_task, Loop, sleep
import lv_utils
from .lv_driver import LVDispDriver, LVTouchInput
from .pages import *
from ..board import Board


class UIApp:
    lv_disp_factor = 5

    def __init__(self, board: Board) -> None:
        self.board: Board = board
        self.width = board.scr_width
        self.height = board.scr_height
        self.pages = []

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
        for page in self.pages:
            page.deinit()
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
        self.setup_pages()
        self.setup_tasks()
        self.run_forever()

    def add_page(self, page: Page):
        if issubclass(page, Page):
            page = page(self.board)
        page.on_load()
        prev_page = None
        if len(self.pages) > 0:
            prev_page = self.pages[-1]
        if prev_page:
            prev_page.set_next_page(page)
            page.set_prev_page(prev_page)
        else:
            lv.screen_load(page)
            page.on_activate()
        self.pages.append(page)
        return page

    def setup_pages(self):
        self.add_page(TextInput)
        self.add_page(SliderPage)
        self.add_page(IMUPage)
        self.add_page(MusicPage)
