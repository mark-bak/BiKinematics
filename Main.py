#standard lib imports
import os
import math
from functools import partial

#Kivy base
from kivy.app import App
from kivy.uix.widget import Widget

#Kivy widgets
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown

#Kivy layouts
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scatter import Scatter
from kivy.uix.popup import Popup

#Kivy properties (kinda like class properties but can interact w/Kivy)
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ListProperty

#Kivy misc
from kivy.factory import Factory
from kivy.uix.behaviors import DragBehavior
from kivy.uix.screenmanager import ScreenManager,Screen

class LoadDialog(FloatLayout):
    ##FILE BROWESER POPUP WIDGET - SEE .kv FILE
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    def get_dir(self):
        return os.getcwd()

class MainPage(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.create_coords()
    #Kivy properties
    link_mode = BooleanProperty(False)
    link_point = ListProperty()

    def create_coords(self):   
        ##Create sidebar coordinate display for every GeoPoint specified in the .kv file
        for wid in list(self.children):
            #for each geo point, create an associated coord display and add to sidebar
            if str(wid.__class__)=="<class '__main__.GeoPoint'>":
                self.ids['sidebar'].add_widget(Coords(ref=wid.ref,point_type=wid.point_type))

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

    ##Geometry shizzle
    def add_link(self):
        self.link_mode = True
        print(self.link_mode)
        print(self.link_point)
        
    
    def on_link_point(self,instance,value):
        lis = value[:]
        if len(lis)>1 and lis[0]==lis[1]:
            lis.pop(0)
        if len(lis)>1:
            print(self.link_mode)
            print(lis)
            link = Link(point_objs = lis)
            self.link_point.clear()
            self.add_widget(link)
            self.link_mode = False
            print(self.link_mode)

class Coords(BoxLayout):
    ##Coordinate box - layout in .kv file
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def type_dropdown(self):
        #might need this
        pass

    #Properties
    txt_x = StringProperty()
    txt_y = StringProperty()
    ref = StringProperty()
    point_type = StringProperty()

class GeoPoint(Scatter):
    ##Draggable point of bike geo

    #Properties
    ref = StringProperty()
    point_type = StringProperty('free')

    def on_pos(self,x,y):
        self.update_coords()

    def update_coords(self):
        ##Update the assoiated coordinate display
        for c in self.parent.walk():
            if str(c.__class__)=="<class '__main__.Coords'>": #bit dodgy but seems to work
                if c.ref == self.ref:
                    c.txt_x = str(round(self.x,2))
                    c.txt_y = str(round(self.y,2))
            if str(c.__class__)=="<class '__main__.Link'>": #bit dodgy but seems to work
                if c.point_objs[0] == self:
                    c.points[0] = self.pos
                if c.point_objs[1] == self:
                    c.points[1] = self.pos

    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.parent.link_mode == True:
            self.parent.link_point.append(self)
        return super(GeoPoint,self).on_touch_down(touch) #do standard scatter touch behaviour

class Link(FloatLayout):

    point_objs = ListProperty()
    points = ListProperty([(0,0),(0,0)])
    length = NumericProperty()





class BiKinematicsApp(App):
    
    def build(self):

        self.screen_manager = ScreenManager()

        self.main_page = MainPage()
        screen = Screen(name = "Main")
        screen.add_widget(self.main_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def update_graphics(self):
        #maybe put all the linked update stuff in here??
        pass

if __name__ == '__main__':
    app = BiKinematicsApp()
    app.run()