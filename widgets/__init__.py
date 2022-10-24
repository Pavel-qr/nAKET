from kivy.base import EventLoop
from kivy.uix.screenmanager import ScreenManager

import config
from widgets.other import *
from widgets.primary import *


class Naket(ScreenManager):
    ...


class NaketApp(MDApp):
    def build(self):
        # theming
        self.theme_cls.theme_style_switch_animation = True  # not working?!
        self.theme_cls.theme_style = config.default_theme  # 'Light' or 'Dark'
        self.theme_cls.primary_palette = config.default_primary_palette  # e.g. 'Orange'

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
        self.root.ids.settings.ids.group.text = group

    def _keyboard_handler(self, _, key, *_s):
        if key in (27, 1001):
            self.root.current = 'home'
            return True
