#Library imports
import numpy as np

#Custom Imports
#pylint: disable=import-error
from KivyWidgets.links import Link,LinkData
import Solver.geometry as g

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import ListProperty
from kivy.properties import ReferenceListProperty
from kivy.uix.widget import Widget

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
    p2mm = NumericProperty() #just used as a flag for changing scaling factor

    
    def on_p2mm(self,instance,value):
        #print('here')
        self.diameter = self.teeth_to_dia(self.diameter_ref.text)

    def teeth_to_dia(self,str_teeth):
        if not str_teeth or self.mp.px_to_mm == 0:
            return 0
        else:               
            link_len = 12.7
            n_teeth = float(str_teeth)
            dia = link_len / np.sin( np.pi / n_teeth ) *  (1/self.mp.px_to_mm)
            return float(dia)

class Wheel(Widget):

    
    centrepoint = ObjectProperty(None)
    diameter_ref = ObjectProperty(None)
    diameter = NumericProperty(69)
    mp = ObjectProperty(None)
    p2mm = NumericProperty() #just used as a flag for changing scaling factor
    
    def on_p2mm(self,instance,value):
        self.diameter = self.inches_to_mm(self.diameter_ref.text)

    def inches_to_mm(self,str_inch):
        if not str_inch or self.mp.px_to_mm == 0:
            return 0
        else:
            return (float(str_inch)*25.4) * (1/self.mp.px_to_mm)

class Chain(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    chainring = ObjectProperty(None)
    cassette = ObjectProperty(None)
    centres = ListProperty()
    dias = ListProperty()
    x_int_cassette = NumericProperty(0)
    y_int_cassette = NumericProperty(0)
    int_cassette = ReferenceListProperty(x_int_cassette, y_int_cassette)
    x_int_chainring = NumericProperty(1)
    y_int_chainring = NumericProperty(1)
    int_chainring = ReferenceListProperty(x_int_chainring, y_int_chainring)


    def on_centres(self,instance,value):
        self.update_chain_int()

    def on_dias(self,instance,value):
        self.update_chain_int()

    def update_chain_int(self):
        """
        Updates chainline intersection points
        """
        t_lines = g.find_common_circle_tangent( self.cassette.pos,
                                                self.cassette.diameter/2,
                                                self.chainring.pos,
                                                self.chainring.diameter/2)

        p_list = g.find_upper_tangent_points(t_lines,self.cassette.pos,self.chainring.pos)
        self.x_int_cassette = float(p_list[0].x)
        self.y_int_cassette = float(p_list[0].y)
        self.x_int_chainring = float(p_list[1].x)
        self.y_int_chainring = float(p_list[1].y)

        # p_cassette =[]
        # p_chainring = []

        # for line in t_lines:
        #     p_cassette.append(g.find_circle_tangent_intersection(self.cassette.pos,line))
        #     p_chainring.append(g.find_circle_tangent_intersection(self.chainring.pos,line))

        # positive_inds_cassette = [p_cassette.index(point) for point in p_cassette
        #                    if point.y-self.cassette.y > 0]
        # positive_inds_chainring = [p_chainring.index(point) for point in p_chainring
        #                    if point.y-self.chainring.y > 0]

        # ind = [i for i in positive_inds_cassette if i in positive_inds_chainring]
        # if ind:
        #     #only update if we have found a soln for upper chain
        #     ind = ind[0]
