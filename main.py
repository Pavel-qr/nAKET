from typing import List

import pandas as pd
from kivy import require
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.scrollview import ScrollView

from utils import Lesson


class Naket(PageLayout):
    ...


class WTasks(ScrollView):
    def add_tasks(self, tasks: pd.DataFrame | None = None):
        self.ids.Tasks.clear_widgets()

        if tasks is None:
            for _ in range(50):
                self.ids.Tasks.add_widget(WTask())
        else:
            tasks.apply(
                lambda task: self.ids.Tasks.add_widget(WTask(task)),
                axis=1
            )


class WSchedule(ScrollView):
    def add_schedule(self, lessons: List[Lesson] | None = None):
        self.ids.Schedule.clear_widgets()

        if lessons is not None:
            ...
        else:
            for _ in range(50):
                self.ids.Schedule.add_widget(WLesson())


class WTask(BoxLayout):
    """
    Widget representation of task.

    +----------+
    |  teacher |
    |   type   |
    |   name   |
    +----------+
    """

    def __init__(self, task: pd.Series | None = None):
        super(WTask, self).__init__()
        if task is not None:
            self.ids.Teacher.text = task['user_id']
            self.ids.Type.text = task['type_name']
            self.ids.Name.text = task['name']


class WLesson(BoxLayout):
    def __init__(self, lesson: Lesson | None = None):
        super(WLesson, self).__init__()
        if lesson is not None:
            ...


class NaketApp(App):
    def build(self):
        self.title = 'nAKET'
        root = WTasks()
        root.add_tasks(None)
        # root.add_tasks(parse.get_tasks(parse.get_session_token(*config.logindata)))
        return root


if __name__ == '__main__':
    require('2.1.0')
    NaketApp().run()
