import lvgl as lv
from blob import Blob


class LVDispDriver:
    def __init__(self, width, height, factor=5, display=None) -> None:
        self.display = display
        self.disp_drv = lv.display_create(width, height)

        color_format = lv.COLOR_FORMAT.RGB565
        self.pixel_size = lv.color_format_get_size(color_format)
        self.disp_drv.set_color_format(color_format)

        # prepare buffer
        buf_size = width * height * self.pixel_size // factor
        self.buf1 = Blob().malloc_dma(buf_size)
        self.buf2 = Blob().malloc_dma(buf_size)
        self.disp_drv.set_buffers(self.buf1.mv(), self.buf2.mv(), buf_size, lv.DISPLAY_RENDER_MODE.PARTIAL)

        self.disp_drv.set_render_mode(lv.DISPLAY_RENDER_MODE.PARTIAL)
        self.disp_drv.set_flush_cb(self.disp_drv_flush_cb)

    def blit(self, area, data):
        x1 = area.x1
        x2 = area.x2
        y1 = area.y1
        y2 = area.y2

        self.display.block(x1, y1, x2, y2, data)

    def disp_drv_flush_cb(self, disp_drv, area, color_p):
        w = area.x2 - area.x1 + 1
        h = area.y2 - area.y1 + 1
        size = w * h
        data_view = color_p.__dereference__(size * self.pixel_size)

        # blit in background
        if self.blit:
            self.blit(area, data_view)
        self.disp_drv.flush_ready()

    def deinit(self):
        self.buf1.free()
        self.buf2.free()


class LVTouchInput:
    def __init__(self, touch) -> None:
        self.indev_drv = lv.indev_create()
        self.indev_drv.set_type(lv.INDEV_TYPE.POINTER)
        self.indev_drv.set_read_cb(self.indev_drv_read_cb)
        self.touch = touch

    def indev_drv_read_cb(self, indev_drv, data):
        info = self.touch.read()
        if info is None:
            return
        if info.num == 0:
            data.state = lv.INDEV_STATE.RELEASED
            return
        pt = info.points[0]
        if not pt.pressed:
            lv.INDEV_STATE.RELEASED
            return
        data.state = lv.INDEV_STATE.PRESSED
        data.point.x = pt.x
        data.point.y = pt.y
