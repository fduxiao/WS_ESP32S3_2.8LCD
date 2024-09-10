import lvgl as lv
from blob import Blob


class LVDispDriver:
    def __init__(self, width, height, factor=5, blit=None) -> None:

        self.blit = blit

        self.disp_drv = lv.disp_create(width, height)

        color_format = lv.COLOR_FORMAT.RGB565
        self.pixel_size = lv.color_format_get_size(color_format)
        self.disp_drv.set_color_format(color_format)

        # prepare buffer
        buf_size = width * height * self.pixel_size // factor
        self.buf1 = Blob().malloc_dma(buf_size)
        self.buf2 = Blob().malloc_dma(buf_size)
        self.disp_drv.set_draw_buffers(self.buf1.mv(), self.buf2.mv(), buf_size, lv.DISP_RENDER_MODE.PARTIAL)

        # self.disp_drv.set_render_mode(lv.DISPLAY_RENDER_MODE.PARTIAL)
        self.disp_drv.set_flush_cb(self.disp_drv_flush_cb)

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
