import logging
from threading import Thread

from kivymd.uix.boxlayout import MDBoxLayout


class AbstractListItem(MDBoxLayout):
    ...


class UpdatableList:
    def __init__(self):
        self.refreshing = False

    def check_update_scroll(self, view, grid):
        max_pixel = 200
        to_relative = max_pixel / (grid.height - view.height)
        if view.scroll_y > 1.0 + to_relative and not self.refreshing:
            logging.info(f'{self}: Refresh')
            self.do_update()

    def do_update(self):
        Thread(target=self._on_update).start()

    def _on_update(self):
        ...
