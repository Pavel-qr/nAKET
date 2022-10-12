from threading import Thread
from typing import List

import pandas as pd
from kivy import require
from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.swiper import MDSwiperItem, MDSwiper

import config
import parse
from utils import Lesson, number_to_str_time


class AbstractListItem(BoxLayout):
    ...


class UpdatableList:
    def __init__(self):
        self.refreshing = False

    def check_update_scroll(self, view, grid):
        max_pixel = 200
        to_relative = max_pixel / (grid.height - view.height)
        if view.scroll_y > 1.0 + to_relative and not self.refreshing:
            print('refresh')
            Thread(target=self._do_update).start()

    def _do_update(self):
        ...


class WTasks(MDSwiperItem, UpdatableList):
    @mainthread
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

    def _do_update(self):
        self.refreshing = True
        self.add_tasks(parse.get_tasks(parse.get_session_token(*config.logindata)))
        self.refreshing = False


class WSchedule(MDSwiperItem, UpdatableList):
    @mainthread
    def add_schedule(self, lessons: List[Lesson] | None = None):
        self.ids.schedule.clear_widgets()

        if lessons is not None:
            for lesson in lessons:
                self.ids.schedule.add_widget(WLesson(lesson))
        else:
            for _ in range(15):
                self.ids.schedule.add_widget(WLesson())

    def _do_update(self):
        self.refreshing = True
        self.add_schedule(parse.get_group_rasp('М156'))
        self.refreshing = False


class WTask(AbstractListItem):
    def __init__(self, task: pd.Series | None = None, **kwargs):
        super(WTask, self).__init__(**kwargs)
        if task is not None:
            self.ids.teacher.text = task['user_id']
            self.ids.type.text = task['type_name']
            self.ids.name.text = task['name']


class WLesson(AbstractListItem):
    def __init__(self, lesson: Lesson | None = None, **kwargs):
        super(WLesson, self).__init__(**kwargs)
        if lesson is not None:
            self.ids.time.text = number_to_str_time[lesson.number]
            self.ids.name.text = f'{lesson.type}: {lesson.name}'


class Naket(MDSwiper):
    ...


class NaketApp(MDApp):
    def build(self):
        self.title = 'nAKET'
        return Naket()


if __name__ == '__main__':
    require('2.1.0')
    NaketApp().run()
