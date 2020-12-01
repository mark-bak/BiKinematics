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

    #General methods
    def dismiss_popup(self):
        self.mode = 'Main'
        self._popup.dismiss()

    #Load methods
    def open_load_dialog(self):
        content = LoadDialog(load=self.load_bike_data, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
   
    def load_bike_data(self, path, selection):
        filename = selection[0]
        with open(filename) as f:
            data = json.load(f)
            for key in data:
                if data[key]['object']=="GeoPoint":
                    self.add_point(key,data[key]['type'],data[key]['position'])
            for key in data: # needs new loop as all points must be created before links
                if data[key]['object']=="Link":
                    a_ref = data[key]['a']
                    b_ref = data[key]['b']
                    for w in self.walk(): #find points corresponding to ref string
                        if isinstance(w,GeoPoint):
                            if w.ref == a_ref:
                                a = w
                            if w.ref == b_ref:
                                b = w
                    self.add_link(a=a,b=b)
        self.dismiss_popup()

    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.mode == 'Add_Point' and self.collide_point(touch.x,touch.y):
            self.open_point_dialog(touch)
        return super(MainPage,self).on_touch_down(touch) #do standard touch behaviour

    #Save methods
    def open_save_dialog(self):
        content = SaveDialog(save = self.save_bike_data,cancel = self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def save_bike_data(self,filename):
        ind = filename.find('.')
        if ind != -1:
            filename = filename[0:ind]
        filename = filename+'.json'
        save_data = {}
        for w in self.walk():
            if isinstance(w,GeoPoint):
                properties={'object':'GeoPoint','type':w.point_type,'position':w.pos}
                save_data[w.ref]= properties
            if isinstance(w,Link):
                properties={'object':'Link','a':w.a.ref,'b':w.b.ref}
                save_data[w.ref]= properties
        with open(filename,'w') as f:
            json.dump(save_data,f,indent=2)
        self.dismiss_popup()

    #Add point methods
    def point_mode(self):
        #Called on add link button press (see .kv)
        self.mode = 'Add_Point'
        self.info = ': click to add point'

    def delete_point_mode(self):
        self.mode = 'Del_Point'
        self.info = ': click to delete point (must be no link attached)'
    
    def open_point_dialog(self,touch):
        content = PointDialog(add=self.add_point,cancel = self.dismiss_popup,touch = touch)
        self._popup = Popup(title="Add Point", content=content,
                            size_hint=(0.6, 0.3))
        self._popup.open()

    def add_point(self,ref,typ,pos):
        #Called on add button press in point dialog popup (see .kv)
        new_point = GeoPoint(ref = ref,point_type = typ,pos = pos)
        self.add_widget(new_point)
        self.ids['coords_list'].add_widget(Coords(ref=ref,point_type=typ))
        self.dismiss_popup()
        self.info = ': point \'{}\' added'.format(new_point.ref)

    def delete_point(self,point):
        self.remove_widget(point)
        for wid in self.walk():
            if isinstance(wid,Coords):
                if wid.ref==point.ref:
                    self.ids['coords_list'].remove_widget(wid)
        self.info = ': point \'{}\' removed'.format(point.ref)
        self.mode = 'Main'

    #Add link methods
    def link_mode(self):
        self.mode = 'Add_Link'
        self.info = ': {} of 2 points selected'.format(str(len(self.link_points)))

    def delete_link_mode(self):
        self.mode = 'Del_Link'
        self.info = ': click to delete Link'
         
    def on_link_points(self,instance,value):
        objs = value
        self.info = ': {} of 2 points selected'.format(str(len(self.link_points)))
        if len(objs)>1 and objs[0]==objs[1]: # stops acccidentally selecting same point twice
            objs.pop(0)
        if len(objs)>1:
            a = objs[0]
            b = objs[1]
            self.add_link(a,b)
            self.link_points.clear()
            self.mode = 'Main'

    def add_link(self,a,b):
        new_link = Link(a = a, b = b)
        new_link.points = [a.pos,b.pos]
        self.add_widget(new_link)
        self.ids['links_list'].add_widget(LinkData(ref = new_link.ref, len_txt = str(new_link.length)))
        self.info = ': link \'{}\' added'.format(new_link.ref)

    def delete_link(self,link):
        self.remove_widget(link)
        for wid in self.walk():
            if isinstance(wid,LinkData):
                if wid.ref==link.ref:
                    self.ids['links_list'].remove_widget(wid)
        self.info = ': link \'{}\' removed'.format(link.ref)
        self.mode = 'Main'


class LoadDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    def get_dir(self):
        return os.getcwd()

class SaveDialog(BoxLayout):
    save = ObjectProperty(None)
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
        ##Update the associated coordinate display and links
        if self.parent != None:
            for w in self.parent.walk():
                if isinstance(w,Coords):
                    if w.ref == self.ref:
                        w.txt_x = str(round(self.x))
                        w.txt_y = str(round(self.y))
                if isinstance(w,Link): 
                    if w.a == self:
                        w.points[0] = self.pos
                    if w.b == self:
                        w.points[1] = self.pos
                    w.update_length()

    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.collide_point(touch.x,touch.y):
            print('touch '+self.ref)
            if self.parent.mode == 'Add_Link': #if in Add_Link mode, add this to the selection list
                self.parent.link_points.append(self)
            if self.parent.mode =='Del_Point':
                self.parent.delete_point(self)
        return super(GeoPoint,self).on_touch_down(touch) #do standard scatter touch behaviour

class Link(Widget):

    a = ObjectProperty(None)
    b = ObjectProperty(None)
    points = ListProperty()
    length = NumericProperty()
    ref = StringProperty()
    midpoint = ListProperty([0,0])

    def update_length(self):
        new_len = float(np.linalg.norm([self.a.x-self.b.x,self.a.y-self.b.y]))
        self.length = new_len
        self.midpoint = self.a.x+(self.b.x-self.a.x)/2,self.a.y+(self.b.y-self.a.y)/2
        if self.parent != None:
            for w in self.parent.walk():
                if isinstance(w,LinkData):
                    if w.ref == self.ref:
                        w.len_txt = str(round(new_len,2))
        return new_len

    
    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.collide_point(touch.x,touch.y):
            print('touch '+self.ref)
            if self.parent.mode == 'Del_Link': #if in Add_Link mode, add this to the selection list
                self.parent.delete_link(self)
        return super(Link,self).on_touch_down(touch) #do standard scatter touch behaviour


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