#Standard Imports
import json

#Custom Widget Imports
#pylint: disable=import-error
from KivyWidgets.links import Link
from KivyWidgets.links import LinkData
from KivyWidgets.dialogs import LoadDialog
from KivyWidgets.dialogs import SaveDialog
from KivyWidgets.dialogs import PointDialog
from KivyWidgets.points import Point
from KivyWidgets.points import PointData

#Kivy Layouts
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty

#Kivy Language Tools
from kivy.lang.builder import Builder

Builder.load_file("KivyWidgets/mainpage.kv")

class MainPage(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    #Kivy properties
    mode = StringProperty('Main')
    info = StringProperty()
    link_points = ListProperty()

    #General methods
    def dismiss_popup(self):
        self.mode = 'Main'
        self._popup.dismiss()

    #User input methods
    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.mode == 'Add_Point' and self.collide_point(touch.x,touch.y):
            self.open_point_dialog(touch)
        return super(MainPage,self).on_touch_down(touch) #do standard touch behaviour

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
                        if isinstance(w,Point):
                            if w.ref == a_ref:
                                a = w
                            if w.ref == b_ref:
                                b = w
                    self.add_link(a=a,b=b)
        self.dismiss_popup()

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
            if isinstance(w,Point):
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
        new_point = Point(ref = ref,point_type = typ,pos = pos)
        self.add_widget(new_point)
        self.ids['coords_list'].add_widget(PointData(ref=ref,point_type=typ))
        self.dismiss_popup()
        self.info = ': point \'{}\' added'.format(new_point.ref)

    def delete_point(self,point):
        self.remove_widget(point)
        for wid in self.walk():
            if isinstance(wid,PointData):
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
        self.ids['links_list'].add_widget(LinkData(ref = new_link.ref, len_txt = str(round(new_link.length,2))))
        self.info = ': link \'{}\' added'.format(new_link.ref)

    def delete_link(self,link):
        self.remove_widget(link)
        for wid in self.walk():
            if isinstance(wid,LinkData):
                if wid.ref==link.ref:
                    self.ids['links_list'].remove_widget(wid)
        self.info = ': link \'{}\' removed'.format(link.ref)
        self.mode = 'Main'