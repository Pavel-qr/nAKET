import parse
from kivy.app import App
from kivy.uix.widget import Widget
from kivy import require


class Naket(Widget):
    ...


class NaketApp(App):
    def build(self):
        self.title = 'nAKET'
        return Naket()


if __name__ == '__main__':
    require('2.1.0')
    NaketApp().run()
