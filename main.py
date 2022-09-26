import parse
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy import require


class Naket(AnchorLayout):
    def __init__(self, **kwargs):
        super(Naket, self).__init__(**kwargs)


class NaketApp(App):
    def build(self):
        self.title = 'nAKET'
        return Naket()


if __name__ == '__main__':
    require('2.1.0')
    NaketApp().run()
