#Kivy Base
from kivy.app import App
import os, sys
from kivy.resources import resource_add_path, resource_find
if hasattr(sys, '_MEIPASS'):
    resource_add_path(sys._MEIPASS)
#Custom Widget Imports
#pylint: disable=import-error
#import KivyWidgets
from KivyWidgets.mainpage import MainPage
from KivyWidgets.plotpage import PlotPage

#Kivy ScreenManager
from kivy.uix.screenmanager import ScreenManager,Screen

class BiKinematicsApp(App):
    def build(self):

        self.sm = ScreenManager()

        self.main_page = MainPage()
        self.plot_page = PlotPage()

        screen = Screen(name = "Main")
        screen.add_widget(self.main_page)
        self.sm.add_widget(screen)
        screen = Screen(name = "Plot")
        screen.add_widget(self.plot_page)
        self.sm.add_widget(screen)

        return self.sm

if __name__ == '__main__':
    #added for PyInstaller to find .kv files
    app = BiKinematicsApp()
    app.run()