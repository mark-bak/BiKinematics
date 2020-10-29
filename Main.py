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

from kivy.properties import ObjectProperty
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

    ##FILE BROWSER POPUP
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        
    def load(self, path, filename):
        self.add_widget(GeoImporter(filename=str(filename[0])))
        self.dismiss_popup()


class GeoImporter(FloatLayout):
    ##GEO IMPORT FROM PICTURE WIDGET  
    filename = ObjectProperty(None)
    def axle_points_press(self):
        self.add_widget(AxlePoints())
            

class AxlePoints(Widget):
    f_axle=ObjectProperty(None)
    r_axle=ObjectProperty(None)

    def on_touch_up(self,touch):
        if self.f_axle.check_collision(self.r_axle):
            self.f_axle.x=self.f_axle.x+25

    pass
    
class GeoPoint(Widget,DragBehavior):
    #def on_touch_move(self,touch):       
     #   if self.collide_point(touch.x,touch.y):
      #      self.center_x=touch.x
       #     self.center_y=touch.y
        #    print(str(self.pos))         
    pass

    def check_collision(self,widg):
        return self.collide_widget(widg)



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