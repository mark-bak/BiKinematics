#standard lib imports
import os
import math
from functools import partial
import numpy as np
import json

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
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ListProperty

#Kivy misc
from kivy.factory import Factory
from kivy.uix.behaviors import DragBehavior
from kivy.uix.screenmanager import ScreenManager,Screen

class MainPage(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    #Kivy properties
    mode = StringProperty('Main')
    info = StringProperty()

    links = ListProperty()
    points = ListProperty()
    link_points = ListProperty()

    #FILE BROWSER POPUP
    def dismiss_popup(self):
        self.mode = 'Main'
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
   
    def load(self, path, filename):
        #put the stuff to do here
        self.dismiss_popup()

    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.mode == 'Add_Point':
            self.point_dialog(touch)
        return super(MainPage,self).on_touch_down(touch) #do standard touch behaviour

    ##Geometry shizzle
    def point_mode(self):
        self.mode = 'Add_Point'
        self.info = ': click to add point'
    
    def point_dialog(self,touch):
        content = PointDialog(add=self.add_point,cancel = self.dismiss_popup,touch = touch)
        self._popup = Popup(title="Add Point", content=content,
                            size_hint=(0.6, 0.3))
        self._popup.open()

    def add_point(self,touch,ref,typ):
        new_point = GeoPoint(ref = ref,point_type = typ,pos = touch.pos)
        self.add_widget(new_point)
        self.ids['coords_list'].add_widget(Coords(ref=ref,point_type=typ))
        self.dismiss_popup()
        self.info = ': point \'{}\' added'.format(new_point.ref)

    def link_mode(self):
        self.mode = 'Add_Link'
        self.info = ': {} of 2 points selected'.format(str(len(self.link_points)))
         
    def on_link_points(self,instance,value):
        objs = value
        self.info = ': {} of 2 points selected'.format(str(len(self.link_points)))
        if len(objs)>1 and objs[0]==objs[1]: # stops acccidentally selecting same point twice
            objs.pop(0)
        if len(objs)>1:
            a = objs[0]
            b = objs[1]
            new_link = Link(a = a, b = b)
            new_link.points = [a.pos,b.pos]
            self.link_points.clear()
            self.add_widget(new_link)
            self.mode = 'Main'
            self.ids['links_list'].add_widget(LinkData(ref = new_link.ref, len_txt = str(new_link.length)))
            self.info = ': link \'{}\' added'.format(new_link.ref)

class LoadDialog(FloatLayout):
    #FILE BROWESER POPUP WIDGET - SEE .kv FILE
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    def get_dir(self):
        return os.getcwd()

class PointDialog(BoxLayout):
    add = ObjectProperty(None)
    cancel = ObjectProperty(None)
    touch = ObjectProperty(None)
    #layout defined in .kv file
    pass

class Coords(BoxLayout):
    ##Coordinate box - layout in .kv file
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    #Properties
    txt_x = StringProperty()
    txt_y = StringProperty()
    ref = StringProperty()
    point_type = StringProperty()

    def type_dropdown(self):
        #might need this
        pass

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
        if self.parent != None: # bobge for now - will sort later
            for c in self.parent.walk():
                if str(c.__class__)=="<class '__main__.Coords'>": #bit dodgy but seems to work - should probs change to c.ids[] or something
                    if c.ref == self.ref:
                        c.txt_x = str(round(self.x))
                        c.txt_y = str(round(self.y))
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
            if self.parent.mode == 'Add_Link': #if in Add_Link mode, add this to the selection list
                self.parent.link_points.append(self)
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