#Standard Imports
import numpy as np

#Kivy Widgets
from kivy.uix.widget import Widget
#Kivy Layouts
from kivy.uix.boxlayout import BoxLayout

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty

#Kivy Language Tools
from kivy.lang.builder import Builder

Builder.load_file("KivyWidgets\\links.kv")

class Link(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #self.points = [self.a.pos,self.b.pos]
        #self.update_length()

    a = ObjectProperty(None)
    b = ObjectProperty(None)
    link_data = ObjectProperty(None)
    points = ListProperty()
    length = NumericProperty()
    name = StringProperty(None)
    midpoint = ListProperty([0,0])
   
    def on_points(self,instance,value):
        new_len = float(np.linalg.norm([self.a.x-self.b.x,self.a.y-self.b.y]))
        new_mid = self.a.x+(self.b.x-self.a.x)/2,self.a.y+(self.b.y-self.a.y)/2
        self.length = new_len
        self.midpoint = new_mid        

    def on_touch_down(self,touch):
        #custom touch behaviour
        if self.collide_point(touch.x,touch.y):
            print('touch '+self.name)
            if self.parent.mode == 'Del_Link': #if in Add_Link mode, add this to the selection list
                self.parent.delete_link(self)
        return super(Link,self).on_touch_down(touch) #do standard scatter touch behaviour

class LinkData(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    #Properties
    mp = ObjectProperty(None)
    len_txt = StringProperty()
    link = ObjectProperty(None)