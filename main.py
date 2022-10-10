from threading import Thread
from time import sleep
from typing import List

import pandas as pd
from kivy import require
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.swiper import MDSwiperItem, MDSwiper

from utils import Lesson


class AbstractListItem(BoxLayout):
    ...


class WTasks(MDSwiperItem):
    def add_tasks(self, tasks: pd.DataFrame | None = None):
        self.ids.tasks.clear_widgets()
        if tasks is not None:
            tasks.apply(
                lambda task: self.ids.tasks.add_widget(WTask(task)),
                axis=1
            )
        else:
            for _ in range(15):
                self.ids.tasks.add_widget(WTask())

    def check_update_scroll(self, view, grid):
        max_pixel = 200
        to_relative = max_pixel / (grid.height - view.height)
        if view.scroll_y < 1.0 + to_relative or self.refreshing:
            return

        print('refresh')
        self.do_update()

    def do_update(self):
        Thread(target=self._do_update()).start()

    def _do_update(self):
        self.refreshing = True
        self.add_tasks(None)
        self.refreshing = False


class WSchedule(MDSwiperItem):
    def add_schedule(self, lessons: List[Lesson] | None = None):
        self.ids.schedule.clear_widgets()

        if lessons is not None:
            ...
        else:
            for _ in range(50):
                self.ids.schedule.add_widget(WLesson())

    def check_update_scroll(self, view, grid):
        max_pixel = 200
        to_relative = max_pixel / (grid.height - view.height)
        if view.scroll_y < 1.0 + to_relative or self.refreshing:
            return

        print('refresh')
        self.do_update()

    def do_update(self):
        Thread(target=self._do_update()).start()

    def _do_update(self):
        self.refreshing = True
        self.add_schedule(None)
        self.refreshing = False


class WTask(AbstractListItem):
    def __init__(self, task: pd.Series | None = None, **kwargs):
        super(WTask, self).__init__(**kwargs)
        if task is not None:
            self.ids.teacher.text = StringProperty(task['user_id'])
            self.ids.type.text = StringProperty(task['type_name'])
            self.ids.name.text = StringProperty(task['name'])


class WLesson(AbstractListItem):
    def __init__(self, lesson: Lesson | None = None, **kwargs):
        super(WLesson, self).__init__(**kwargs)
        if lesson is not None:
            ...


class Naket(MDSwiper):
    ...


class NaketApp(MDApp):
    def build(self):
        self.title = 'nAKET'
        return Naket()


if __name__ == '__main__':
    require('2.1.0')
    NaketApp().run()
