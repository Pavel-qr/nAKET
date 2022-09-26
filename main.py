from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy import require

from random import randint
import parse


class Naket(AnchorLayout):
    def add_tasks(self):
        # todo remove all tasks here
        ...

        for _ in range(30):
            self.ids.Tasks.add_widget(Button(
                text=f'Task №{randint(34545, 1838581)}.',
                size_hint_y=None, height=40
            ))

    def add_schedule(self):
        # todo remove all schedules here
        ...

        for _ in range(7):
            self.ids.Schedule.add_widget(Label(
                text='Day of the week or something',
                size_hint_y=None, height=40
            ))
            for _ in range(5):
                self.ids.Schedule.add_widget(Button(
                    text=f'Some couple',
                    size_hint_y=None, height=40
                ))


class NaketApp(App):
    def build(self):
        self.title = 'nAKET'
        root = Naket()
        root.add_tasks()
        root.add_schedule()
        return root


if __name__ == '__main__':
    require('2.1.0')
    NaketApp().run()
