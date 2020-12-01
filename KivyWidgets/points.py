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

class PointData(BoxLayout):
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

class Point(Scatter):
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
                if isinstance(w,PointData):
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
        return super(Point,self).on_touch_down(touch) #do standard scatter touch behaviour