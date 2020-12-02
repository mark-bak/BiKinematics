#Custom Widget Imports
#pylint: disable=import-error
from KivyWidgets.links import Link 

#Kivy Widgets
from kivy.uix.widget import Widget
#Kivy Layouts
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

#Kivy Language Tools
from kivy.lang.builder import Builder

Builder.load_file("KivyWidgets/points.kv")

class Point(Scatter):
    ##Draggable point of bike geo

    #Properties
    name = StringProperty()
    point_type = StringProperty()
    point_data = ObjectProperty(None)

    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.collide_point(touch.x,touch.y):
            print('touch '+self.name)
            if self.parent.mode == 'Add_Link': #if in Add_Link mode, add this to the selection list
                self.parent.link_points.append(self)
            if self.parent.mode =='Del_Point':
                self.parent.delete_point(self)
        return super(Point,self).on_touch_down(touch) #do standard scatter touch behaviour

class PointData(BoxLayout):
    ##Coordinate box - layout in .kv file
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    #Properties
    point = ObjectProperty(None)
    txt_x = StringProperty()
    txt_y = StringProperty()
    name = StringProperty()
    point_type = StringProperty()

    def type_dropdown(self):
        #might need this
        pass

