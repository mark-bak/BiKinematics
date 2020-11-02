import os

from kivy.app import App
from kivy.uix.widget import Widget

from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scatter import Scatter

from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import NumericProperty

from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.uix.behaviors import DragBehavior

from kivy.uix.screenmanager import ScreenManager,Screen

class LoadDialog(FloatLayout):
    ##FILE BROWESER POPUP WIDGET - SEE .kv FILE
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    def get_dir(self):
        return os.getcwd()

class MainPage(FloatLayout):
    #Properties
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #self.create_coords()

    def create_coords(self):
        for wid in list(self.children):
            if str(wid.__class__)=="<class '__main__.GeoPoint'>":
                print(wid.x)
                self.ids['sidebar'].add_widget(Coords(txt='create_coord_test',wid=wid))


    ##FILE BROWSER POPUP
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        
    def load(self, path, filename):
        #put the stuff to do here
        self.dismiss_popup()

class Coords(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    #Properties
    txt = StringProperty() #Label text 
    txt_x = StringProperty()
    txt_y = StringProperty()
    #wid = ObjectProperty(None)

    #def update_string(self,wid):
    #    self.txt_x=str(wid.x)

class GeoPoint(Scatter):
    #Properties
    txt = StringProperty() #Label text

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