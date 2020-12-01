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

Builder.load_file("KivyWidgets/links.kv")

class Link(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.update_length()

    a = ObjectProperty(None)
    b = ObjectProperty(None)
    points = ListProperty()
    length = NumericProperty()
    ref = StringProperty()
    midpoint = ListProperty([0,0])

    def update_length(self):
        new_len = float(np.linalg.norm([self.a.x-self.b.x,self.a.y-self.b.y]))
        new_mid = self.a.x+(self.b.x-self.a.x)/2,self.a.y+(self.b.y-self.a.y)/2
        self.length = new_len
        self.midpoint = new_mid
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

class LinkData(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    #Properties
    len_txt = StringProperty()
    ref = StringProperty()