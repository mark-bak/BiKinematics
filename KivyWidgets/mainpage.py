#Standard Imports
import json
import os

#Custom Widget Imports
#pylint: disable=import-error
from KivyWidgets.links import Link
from KivyWidgets.links import LinkData
from KivyWidgets.dialogs import LoadDialog
from KivyWidgets.dialogs import SaveDialog
from KivyWidgets.dialogs import PointDialog
from KivyWidgets.dialogs import SimulateDialog
from KivyWidgets.points import Point
from KivyWidgets.points import PointData
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from Solver.bike import Bike


from Solver.bike import Bike

#Kivy Layouts
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty

#Kivy Language Tools
from kivy.lang.builder import Builder
from kivy.core.window import Window

Builder.load_file("KivyWidgets\\mainpage.kv")

class MainPage(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #Window.maximize()
        Window.bind(on_resize=self.on_window_resize)
        self.sidebar_width = self.ids['sidebar'].width
        self.topbar_height = self.ids['topbar'].height
        self.info_text_height = self.ids['current_mode'].height

    #Kivy properties
    mode = StringProperty('Main')
    info = StringProperty()
    link_points = ListProperty()

    px_to_mm = NumericProperty(1)

    cur_width = NumericProperty(Window.width)
    cur_height = NumericProperty(Window.height)
    sidebar_width = NumericProperty()
    topbar_height = NumericProperty()
    info_text_height = NumericProperty()

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

    def on_window_resize(self, window, width, height): #Resizes geo elements on window resize
        cur_imf_width = self.cur_width - self.sidebar_width 
        new_imf_width = width - self.sidebar_width

        cur_imf_height = self.cur_height - self.topbar_height 
        new_imf_height = height - self.topbar_height

        height_offset = 0

        for w in self.walk():
            if isinstance(w,Point):
                w.scale_with_window(cur_imf_width,
                                    new_imf_width,
                                    cur_imf_height,
                                    new_imf_height,
                                    height_offset,)

        self.cur_width = width
        self.cur_height = height

        self.update_px_mm_conversion()

    def update_px_mm_conversion(self):
        fw = None
        rw = None
        for wid in self.children:
            if isinstance(wid,Point):
                if wid.point_type == 'front_wheel':
                    fw = wid
                if wid.point_type == 'rear_wheel':
                    rw = wid
        if fw != None and rw != None:
            wbase_px = fw.x-rw.x
            try:
                wbase_mm = float(self.ids['params_list'].wheelbase)
            except:
                wbase_mm = 0
            self.px_to_mm = wbase_mm / wbase_px
        else:
            self.px_to_mm = 1
        
        print(self.px_to_mm)

    def goto_plot(self):
        #  
        self.parent.manager.current = 'Plot' #lol what a mess this line is
    
    #Top menu dropdown load functions - can probably condense this into
    #one function but had trouble with calling desired dropdown class from .kv file
    def show_load_dropdown(self,parent):
        dropdown = LoadDropDown(mp=self)
        dropdown.open(parent)

    def show_add_geo_dropdown(self,parent):
        dropdown = AddGeoDropDown(mp=self)
        dropdown.open(parent)

    def show_delete_dropdown(self,parent):
        dropdown = DeleteDropDown(mp=self)
        dropdown.open(parent)
    
    def show_anal_dropdown(self,parent):
        dropdown = AnalDropDown(mp=self)
        dropdown.open(parent)

    #User input methods
    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.mode == 'Add_Point' and self.collide_point(touch.x,touch.y):
            self.open_point_dialog(touch)
        return super(MainPage,self).on_touch_down(touch) #do standard touch behaviour

    #Load methods
    def open_load_dialog(self):
        content = LoadDialog(load=self.load_bike_data, cancel=self.dismiss_popup,directory = "\\SaveFiles")
        self._popup = ThemePopup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
   
    def load_bike_data(self, path, selection):
        filename = selection[0]
        with open(filename) as f:
            data = json.load(f)
            for key in data:
                if data[key]['object']=="Point":
                    self.add_point(key,data[key]['type'],data[key]['position'])
            for key in data: #needs new loop as all points must be created before links
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
        self._popup = ThemePopup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def save_bike_data(self,filename,path):
        filename = filename.replace(path+"\\","") #remove path from filename
        ind = filename.find('.') #remove file extension
        if ind != -1:
            filename = filename[0:ind]
        filename = "{}\\{}.json".format(path,filename) #put in path with .json ext
        save_data = self.create_bike_data(sf=1)
        with open(filename,'w') as f:
            json.dump(save_data,f,indent=2)
        self.dismiss_popup()

    def create_bike_data(self,sf):
        data = {}
        for w in self.walk():
            if isinstance(w,Point):
                properties={'object':'Point','type':w.point_type,'position':tuple([w.x*sf,w.y*sf])}
                data[w.name]= properties
            if isinstance(w,Link):
                properties={'object':'Link','a':w.a.name,'b':w.b.name}
                data[w.name]= properties
        return data

    #Image methods
    def open_image_dialog(self):
        content = LoadDialog(load=self.load_image, cancel=self.dismiss_popup,directory = "\\ImageFiles")
        self._popup = ThemePopup(title="Load file", content=content,
                    size_hint=(0.9, 0.9))
        self._popup.open()

    def load_image(self,path,selection):
        filename = selection[-1]
        self.clear_image()
        self.ids['image_frame'].add_widget(Image(source=filename,
                                                 pos=self.ids['image_frame'].pos))
        self.dismiss_popup()

    def clear_image(self):
        for child in self.ids['image_frame'].children:
            self.ids['image_frame'].remove_widget(child)

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
        self._popup = ThemePopup(title="Add Point", content=content,
                            size_hint=(None,None),size = (400,150),
                            pos_hint={  'x': touch.x / self.width, 
                                        'y': touch.y / self.height}) 
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
        self.update_px_mm_conversion()

    def delete_point(self,point):
        self.ids['points_list'].remove_widget(point.point_data)
        self.remove_widget(point)
        self.info = ': point \'{}\' removed'.format(point.name)
        self.mode = 'Main'
        self.update_px_mm_conversion()

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
        new_link_data = LinkData(link = new_link,mp=self)
        new_link.link_data = new_link_data

        self.add_widget(new_link)
        self.ids['links_list'].add_widget(new_link_data)
        self.info = ': link \'{}\' added'.format(new_link.name)

    def delete_link(self,link):
        self.ids['links_list'].remove_widget(link.link_data)
        self.remove_widget(link)
        self.mode = 'Main'

    #Simulate methods
    def open_sim_dialog(self):
        content = SimulateDialog(simulate=self.simulate,cancel = self.dismiss_popup)
        self._popup = ThemePopup(title="Simulate", content=content,
                            size_hint=(None,None),size = (400,150)) 
        self._popup.open()

    def simulate(self,filename,desired_travel):
        desired_travel = float(desired_travel)
        sim_data = self.create_bike_data(sf = self.px_to_mm)
        b = Bike(sim_data)
        sol_name = 'Single_Sim'
        b.get_suspension_motion(desired_travel,sol_name)
        b.save_solution_csv(sol_name,filename)
        self.dismiss_popup()
        self.info = ': Simulation: {} complete'.format(filename)

#Dropdown style classes - see.kv for formatting
class LoadDropDown(DropDown):
    mp = ObjectProperty(None)  

class AddGeoDropDown(DropDown):
    mp = ObjectProperty(None) 

class DeleteDropDown(DropDown):
    mp = ObjectProperty(None)

class AnalDropDown(DropDown):
    mp = ObjectProperty(None)

#Custom popup hacky thing - see .kv
class ThemePopup(Popup):
    bg_color = ListProperty([0,0,0,1])

class TopbarButton(Button):
    pass



