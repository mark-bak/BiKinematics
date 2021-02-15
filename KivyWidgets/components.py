
import numpy as np

#Custom Imports
#pylint: disable=import-error
from KivyWidgets.links import Link,LinkData
from kivy.uix.widget import Widget

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty

#Kivy Language Tools
from kivy.lang.builder import Builder

Builder.load_file("KivyWidgets\\components.kv")

#Shock is basicaly the same as a link - however have created seperate object for clarity and also in
#case more functionality needed later
class Shock(Link):
    Colour_Picker = ObjectProperty(None)
    pass

class ShockData(LinkData):
    pass

class Cog(Widget):
    centrepoint = ObjectProperty(None)
    diameter_ref = ObjectProperty(None)
    diameter = NumericProperty(69)
    mp = ObjectProperty(None)

    def teeth_to_dia(self,str_teeth):
        if not str_teeth or self.mp.px_to_mm == 0:
            return 0
        else:               
            link_len = 12.7
            n_teeth = float(str_teeth)
            dia = link_len / np.sin( np.pi / n_teeth ) *  (1/self.mp.px_to_mm)
            return float(dia)