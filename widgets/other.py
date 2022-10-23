import pandas as pd
from kivy.clock import mainthread
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp

import parse
from utils import Session, PASS_REAL_VALUES
from widgets.abstract import UpdatableList
from widgets.items import WSession, WTeacher, WMaterial


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
                *MDApp.get_running_app().get_login_password()
            ))
            if PASS_REAL_VALUES else None
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
                MDApp.get_running_app().get_group()
            )
            if PASS_REAL_VALUES else None
        )
        self.refreshing = False


class WTeachers(Screen):
    def __init__(self, **kwargs):
        super(WTeachers, self).__init__(**kwargs)
        self.data = parse.get_teachers()
        self.filter = self.data

    def add_teachers(self):
        self.ids.teachers.clear_widgets()

        self.data.where(self.filter).apply(
            lambda teacher: self.ids.teachers.add_widget(WTeacher(teacher)),
            axis=1
        )


class WSettings(Screen):
    ...


class WCalendarExport(Screen):
    ...
