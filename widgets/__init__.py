from kivy.base import EventLoop
from kivy.uix.screenmanager import ScreenManager

import config
from widgets.primary import *
from widgets.settings import *


class Naket(ScreenManager):
    ...


class NaketApp(MDApp):
    def build(self):
        # self.theme_cls.theme_style = "Dark"  # change background to black
        self.title = 'nAKET'
        self.root = Naket()
        self.set_group('4142')
        self.set_login_password(*config.logindata)
        for screen_id in 'tasks', 'schedule', 'sessions', 'materials':
            self.root.ids[screen_id].do_update()
        return self.root

    def on_start(self):
        EventLoop.window.bind(on_keyboard=self._keyboard_handler)

    def get_login_password(self):
        return (
            self.root.ids.settings.ids.login.text,
            self.root.ids.settings.ids.password.text
        )

    def set_login_password(self, login, password):
        self.root.ids.settings.ids.login.text = login
        self.root.ids.settings.ids.password.text = password

    def get_group(self):
        return self.root.ids.settings.ids.group.text

    def set_group(self, group):
        print(self.root)
        print(self.root.ids)
        print(self.root.ids.settings)
        print(self.root.ids.settings.ids)
        print(self.root.ids.settings.ids.group)
        print(self.root.ids.settings.ids.group.text)
        self.root.ids.settings.ids.group.text = group

    def _keyboard_handler(self, _, key, *_s):
        if key in (27, 1001):
            self.root.current = 'home'
            return True
