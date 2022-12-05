import pandas as pd
from kivy.clock import mainthread
from kivymd.app import MDApp
from kivymd.uix.swiper import MDSwiperItem

import parse
from utils import Lesson
from abstract import UpdatableList
from items import WLesson, WTask


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

    def _on_update(self):
        self.refreshing = True
        self.add_tasks(
            parse.get_tasks(parse.get_session_token(
                MDApp.get_running_app().login,
                MDApp.get_running_app().password
            ))
            if MDApp.get_running_app().pass_real_values
            else None
        )
        self.refreshing = False


class WSchedule(MDSwiperItem, UpdatableList):
    @mainthread
    def add_schedule(self, lessons: list[Lesson] | None = None):
        self.ids.schedule.clear_widgets()

        if lessons is not None:
            for lesson in lessons:
                self.ids.schedule.add_widget(WLesson(lesson))
        else:
            for _ in range(15):
                self.ids.schedule.add_widget(WLesson())

    def _on_update(self):
        self.refreshing = True
        self.add_schedule(
            parse.get_group_rasp(
                MDApp.get_running_app().group
            )
            if MDApp.get_running_app().pass_real_values
            else None
        )
        self.refreshing = False
