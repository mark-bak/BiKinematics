#standard lib imports
import os
import math
from functools import partial
import numpy as np

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
        print('adding link!')
       
    
    def on_link_point(self,instance,value):
        objs = value[:]
        if len(objs)>1 and objs[0]==objs[1]: # stops acccidentally selecting same point twice
            objs.pop(0)
        if len(objs)>1:
            a = objs[0]
            b = objs[1]
            new_link = Link(a = a, b = b)
            new_link.points = [a.pos,b.pos]
            self.link_point.clear()
            self.add_widget(new_link)
            self.link_mode = False
            self.ids['sidebar'].add_widget(LinkData(ref = new_link.ref, len_txt = str(new_link.length)))
            print('link {} added'.format(new_link.ref))

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

class LinkData(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    #Properties
    len_txt = StringProperty()
    ref = StringProperty()

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
            if str(c.__class__)=="<class '__main__.Coords'>": #bit dodgy but seems to work - should probs change to c.ids[] or something
                if c.ref == self.ref:
                    c.txt_x = str(round(self.x,2))
                    c.txt_y = str(round(self.y,2))
            if str(c.__class__)=="<class '__main__.Link'>": #bit dodgy but seems to work
                if c.a == self:
                    c.points[0] = self.pos
                if c.b == self:
                    c.points[1] = self.pos
                c.update_length()


    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.collide_point(touch.x,touch.y):
            #print('touch '+self.ref)
            if self.parent.link_mode == True: #if in add_link mode, add this to the selection list
                self.parent.link_point.append(self)
        return super(GeoPoint,self).on_touch_down(touch) #do standard scatter touch behaviour

class Link(Widget):

    a = ObjectProperty(None)
    b = ObjectProperty(None)
    points = ListProperty()
    length = NumericProperty()
    ref = StringProperty()

    def update_length(self):
        new_len = float(np.linalg.norm([self.a.x-self.b.x,self.a.y-self.b.y]))
        if self.parent != None:
            for c in self.parent.walk():
                if str(c.__class__)=="<class '__main__.LinkData'>": #bit dodgy but seems to work
                    if c.ref == self.ref:
                        c.len_txt = str(round(new_len,2))
        return new_len


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