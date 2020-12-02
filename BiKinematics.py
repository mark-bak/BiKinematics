#Kivy Base
from kivy.app import App

#Custom Widget Imports
from KivyWidgets.mainpage import MainPage

#Kivy ScreenManager
from kivy.uix.screenmanager import ScreenManager,Screen

class BiKinematicsApp(App):
    def build(self):

        self.screen_manager = ScreenManager()
        self.main_page = MainPage()
        screen = Screen(name = "Main")
        screen.add_widget(self.main_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

if __name__ == '__main__':
    app = BiKinematicsApp()
    app.run()