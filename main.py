from kivy.app import App
from kivy.core.window import Window
from src.ui.converter import PngToJpgConverter

class PngToJpgConverterApp(App):
    def build(self):
        Window.size = (800, 900)
        return PngToJpgConverter()

if __name__ == '__main__':
    PngToJpgConverterApp().run()