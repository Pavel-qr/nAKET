import pandas as pd
from kivy.clock import mainthread
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem

import parse
from utils import Session
from abstract import UpdatableList
from items import WSession, WTeacher, WMaterial


class WMaterials(Screen, UpdatableList):
    @mainthread
    def add_materials(self, materials: pd.DataFrame | None = None):
        self.ids.materials.clear_widgets()

        if materials is not None:
            materials.apply(
                lambda material: self.ids.materials.add_widget(WMaterial(material)),
                axis=1
            )
        else:
            for _ in range(15):
                self.ids.materials.add_widget(WMaterial())

    def _on_update(self):
        self.refreshing = True
        self.add_materials(
            parse.get_materials(parse.get_session_token(
                MDApp.get_running_app().login,
                MDApp.get_running_app().password
            ))
            if MDApp.get_running_app().pass_real_values
            else None
        )
        self.refreshing = False


class WSessions(Screen, UpdatableList):
    @mainthread
    def add_sessions(self, sessions: list[Session] | None = None):
        self.ids.sessions.clear_widgets()

        if sessions is not None:
            for session in sessions:
                self.ids.sessions.add_widget(WSession(session))
        else:
            for _ in range(15):
                self.ids.sessions.add_widget(WSession())

    def _on_update(self):
        self.refreshing = True
        self.add_sessions(
            parse.get_sessions(
                MDApp.get_running_app().group
            )
            if MDApp.get_running_app().pass_real_values
            else None
        )
        self.refreshing = False


class WTeachers(Screen):
    def __init__(self, **kwargs):
        super(WTeachers, self).__init__(**kwargs)

    def add_teachers(self, search_text: str):
        self.ids.teachers.clear_widgets()

        data = parse.get_teachers(parse.get_session_token(
            MDApp.get_running_app().login,
            MDApp.get_running_app().password
        ), search_text)
        if data is not None and not data[0].empty:
            # todo handle data[1]
            data[0].apply(
                lambda teacher: self.ids.teachers.add_widget(WTeacher(teacher)),
                axis=1
            )
        else:
            self.ids.teachers.add_widget(
                OneLineListItem(text='Nothing')
            )


class WSettings(Screen):
    ...


class WCalendarExport(Screen):
    ...
