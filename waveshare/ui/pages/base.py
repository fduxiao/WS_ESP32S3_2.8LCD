import lvgl as lv


class Page(lv.obj):
    prev_btn = None
    prev_page = None
    next_btn = None
    next_page = None

    def __init__(self, board):
        self.board = board
        super().__init__()

    def on_load(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def set_prev_page(self, page):
        btn = lv.button(self)
        btn.align(lv.ALIGN.TOP_LEFT, 5, 5)
        label = lv.label(btn)
        label.set_text("<")

        def callback(e):
            self.on_deactivate()
            lv.screen_load(page)
            page.on_activate()

        btn.add_event_cb(callback, lv.EVENT.CLICKED, None)
        self.prev_page = page
        self.prev_btn = btn

    def set_next_page(self, page):
        btn = lv.button(self)
        btn.align(lv.ALIGN.TOP_RIGHT, -5, 5)
        label = lv.label(btn)
        label.set_text(">")

        def callback(e):
            self.on_deactivate()
            lv.screen_load(page)
            page.on_activate()

        btn.add_event_cb(callback, lv.EVENT.CLICKED, None)
        self.next_page = page
        self.next_btn = btn

    def deinit(self):
        if self.prev_page is not None:
            del self.prev_page
            del self.prev_btn
        if self.next_page is not None:
            del self.next_page
            del self.next_btn
