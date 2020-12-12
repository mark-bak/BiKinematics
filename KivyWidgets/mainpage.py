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

from Solver.bike import kivy_to_bike,Bike

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

    def clear_all(self):
        for wid in self.walk():
            if isinstance(wid,Point):
                self.delete_point(wid)
            if isinstance(wid,Link):
                self.delete_link(wid)

    def goto_plot(self):
        points_list = []
        links_list = []
        for wid in self.walk():
            if isinstance(wid,Point):
                point_info = {'name':wid.name,'type':wid.point_type,'pos':list(wid.pos)}
                points_list.append(point_info)
            if isinstance(wid,Link):
                link_info = {'name':wid.name,'a':wid.a.name,'b':wid.b.name}
                links_list.append(link_info)
        #bike_data = kivy_to_bike(points_list,links_list,300,1250)
        bike = Bike(points_list,links_list,1200)
        path = bike.find_kinematic_loop()
        print(path)
        self.parent.manager.current = 'Plot' #lol what a mess this line is

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
                            if w.name == a_ref:
                                a = w
                            if w.name == b_ref:
                                b = w
                    self.add_link(a=a,b=b)
        self.dismiss_popup()

    #Save methods
    def open_save_dialog(self):
        content = SaveDialog(save = self.save_bike_data,cancel = self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def save_bike_data(self,filename,path):
        ind = filename.find('.')
        if ind != -1:
            filename = filename[0:ind]
        filename = filename+'.json'
        save_data = {}
        for w in self.walk():
            if isinstance(w,Point):
                properties={'object':'GeoPoint','type':w.point_type,'position':w.pos}
                save_data[w.name]= properties
            if isinstance(w,Link):
                properties={'object':'Link','a':w.a.name,'b':w.b.name}
                save_data[w.name]= properties
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

    def add_point(self,name,typ,pos):
        #Called on Add button press in point dialog popup (see dialogs.kv)
        new_point = Point(name = name,point_type = typ,pos = pos)
        new_point_data = PointData(point = new_point,name=name,point_type=typ)
        new_point.point_data = new_point_data
        self.add_widget(new_point)
        self.ids['points_list'].add_widget(new_point_data)
        self.dismiss_popup()
        self.info = ': point \'{}\' added'.format(new_point.name)

    def delete_point(self,point):
        self.ids['points_list'].remove_widget(point.point_data)
        self.remove_widget(point)
        self.info = ': point \'{}\' removed'.format(point.name)
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
        #called on Add Link button press - see .kv
        new_link = Link(a = a, b = b)
        new_link_data = LinkData(link = new_link)
        new_link.link_data = new_link_data

        self.add_widget(new_link)
        self.ids['links_list'].add_widget(new_link_data)
        self.info = ': link \'{}\' added'.format(new_link.name)

    def delete_link(self,link):
        self.ids['links_list'].remove_widget(link.link_data)
        self.remove_widget(link)
        self.mode = 'Main'

    