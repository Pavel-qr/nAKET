import os

# from cryptography.fernet import Fernet    # todo encrypt config.json file
from kivy.base import EventLoop
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager

from widgets.other import *
from widgets.primary import *


class Naket(ScreenManager):
    ...


class NaketApp(MDApp):
    def __init__(self, **kwargs):
        super(NaketApp, self).__init__(**kwargs)
        # ∨∨∨ during development (replace occurrences with MDApp().user_data_dir or self.user_data_dir on release)
        self.user_data_dir_dev = '.'
        config_path = os.path.join(self.user_data_dir_dev, 'config.json')
        if not os.path.exists(config_path):
            with open(file=config_path, mode='w'):
                pass  # create empty file
            empty_config = JsonStore(config_path)
            empty_config.put('credentials', login='', password='')
            empty_config.put('data', pass_real_values=True)
            empty_config.put('group', group='')
            empty_config.put('theming', default_theme='Dark',
                             default_primary_palette='DeepOrange')
        self.store = JsonStore(config_path)

    def build(self):
        # theming
        self.theme_cls.theme_style_switch_animation = True  # not working?!
        self.theme_cls.theme_style = self.get_default_theme()  # 'Light' or 'Dark'
        self.theme_cls.primary_palette = self.get_default_primary_palette()  # e.g. 'Orange'

        self.title = 'nAKET'
        self.root = Naket()
        for screen_id in 'tasks', 'schedule', 'sessions', 'materials':
            self.root.ids[screen_id].do_update()
        return self.root

    def on_start(self):
        EventLoop.window.bind(on_keyboard=self._keyboard_handler)

    def get_default_primary_palette(self):
        return self.store.get('theming')['default_primary_palette']

    def set_default_primary_palette(self, default_primary_palette):
        # ∨∨∨ todo find a way to purposefully change the key or change the structure of the file
        self.store.put('theming', default_primary_palette=default_primary_palette,
                       default_theme=self.get_default_theme())

    def get_default_theme(self):
        return self.store.get('theming')['default_theme']

    def set_default_theme(self, default_theme):
        # ∨∨∨ todo find a way to purposefully change the key or change the structure of the file
        self.store.put('theming', default_theme=default_theme,
                       default_primary_palette=self.get_default_primary_palette())

    def get_login(self):
        return self.store.get('credentials')['login']

    def set_login(self, login):
        self.store.put('credentials', login=login, password=self.get_password())

    def get_password(self):
        return self.store.get('credentials')['password']

    def set_password(self, password):
        self.store.put('credentials', password=password, login=self.get_login())

    def get_group(self):
        return self.store.get('group')['group']

    def set_group(self, group):
        # todo change file structure
        self.store.put('group', group=group)

    def get_pass_real_values(self):
        return self.store.get('data')['pass_real_values']

    def _keyboard_handler(self, _, key, *_s):
        if key in (27, 1001):
            self.root.current = 'home'
            return True
