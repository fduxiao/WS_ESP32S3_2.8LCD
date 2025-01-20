import lvgl as lv
from asyncio import sleep, create_task
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

    def play_music(self, e):
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
