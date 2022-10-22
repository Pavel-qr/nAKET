import logging

import pandas as pd

from utils import number_to_str_time, Lesson
from widgets.abstract import AbstractListItem


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


class WMaterial(AbstractListItem):
    def __init__(self, material: pd.Series | None = None, **kwargs):
        super(WMaterial, self).__init__(**kwargs)
        if material is not None:
            self.ids.name.text = material['name']
            url = material['url']
            self.ids.url.text = \
                f'[color=0000EE][ref={url}]{url}[/ref][/color]' if url is not None else 'Не указан'
            filelink = material['filelink']
            self.ids.filelink.text = \
                f'[color=0000EE][ref={filelink}]{filelink}[/ref][/color]' if filelink is not None else 'Не указан'


class WSession(AbstractListItem):
    def __init__(self, session: pd.Series | None = None, **kwargs):
        super(WSession, self).__init__(**kwargs)
        if session is not None:
            logging.critical(f'{self}: Not implemented __init__')
            ...


class WTeacher(AbstractListItem):
    def __init__(self, teacher: pd.Series | None = None, **kwargs):
        super(WTeacher, self).__init__(**kwargs)
        if teacher is not None:
            logging.critical(f'{self}: Not implemented __init__')
            ...


