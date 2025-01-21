import lvgl as lv
from asyncio import sleep, create_task, StreamWriter
from .base import Page


class TextInput(Page):
    def __init__(self, board):
        super().__init__(board)
        # keyboard + textarea
        ta = lv.textarea(self)
        ta.set_width(240)
        ta.set_height(70)
        ta.align(lv.ALIGN.CENTER, 0, -70)
        ta.set_text("")

        kb = lv.keyboard(self)
        kb.set_textarea(ta)


class SliderPage(Page):
    def __init__(self, board):
        super().__init__(board)
        slider = lv.slider(self)
        slider.set_width(120)
        slider.align(lv.ALIGN.TOP_MID, 0, 15)

        led1 = lv.led(self)
        led1.align(lv.ALIGN.CENTER, 0, 0)
        led1.set_brightness(slider.get_value() * 2)
        led1.set_size(20, 20)

        slider.add_event_cb(lambda e: led1.set_brightness(slider.get_value() * 2), lv.EVENT.VALUE_CHANGED, None)

        slider2 = lv.slider(self)
        slider2.set_value(100, lv.ANIM.OFF)
        slider2.set_width(120)
        slider2.align(lv.ALIGN.TOP_MID, 0, 100)

        slider2.add_event_cb(lambda e: self.board.blk(0.2 + slider2.get_value() / 100 * 0.8), lv.EVENT.VALUE_CHANGED, None)


class IMUPage(Page):
    def __init__(self, board):
        super().__init__(board)
        label = lv.label(self)
        label.align(lv.ALIGN.TOP_MID, 0, 100)
        label.set_text("imu data:")
        self.imu_label = label
        self.task = None

    def on_activate(self):
        if self.task:
            self.task.cancel()
        self.task = create_task(self.update_imu())

    def on_deactivate(self):
        if self.task is not None:
            self.task.cancel()
            self.task = None

    async def update_imu(self):
        while True:
            (ax, ay, az), (gx, gy, gz) = self.board.read_imu()
            self.imu_label.set_text(f"imu data: {ax:.1f}, {ay:.1f}, {az:.1f}\n"
                                    f"          {gx:.1f}, {gy:.1f}, {gz:.1f}")
            await sleep(0.1)


class MusicPage(Page):
    def __init__(self, board):
        super().__init__(board)

        btn = lv.button(self)
        btn.align(lv.ALIGN.TOP_MID, 0, 50)
        label = lv.label(btn)
        label.set_text("play sound")
        btn.add_event_cb(self.play_music, lv.EVENT.CLICKED, None)

        self.i2s = board.i2s
        self.batch = 5000
        self.step = 1 / self.board.i2s_rate
        self.amp = 1 << (self.board.i2s_bits - 1)
        self.amp /= 4
        self.buf_size = self.board.i2s_buf_size

        self.total_tick = 3 * self.board.i2s_rate
        self.task = None

    def play_music(self, e):
        print("play music")
        if self.task is not None:
            self.task.cancel()
        self.task = create_task(self.play())

    def on_deactivate(self):
        self.task.cancel()
        self.task = None

    def get_samples(self, freq, tick):
        from ulab import numpy as np
        # calculate one batch
        values = np.array(range(self.batch))
        values += tick
        values *= self.step
        values = self.amp * np.sin(values * 2 * np.pi * freq)
        # cast to int16
        values = np.array(values, dtype=np.int16)
        # reshape to make left and right channels
        values = values.reshape((-1, 1))
        values = np.concatenate((values, values), axis=1).reshape(-1)
        values = values.tobytes()
        return values

    async def play(self):
        from rom_data import data_wav
        # freq = 440
        tick = 0
        writter = StreamWriter(self.i2s)
        while tick < len(data_wav):
            # data = self.get_samples(freq, tick)
            data = data_wav[tick:tick+self.batch]
            tick += self.batch
            writter.write(data)
            await writter.drain()
