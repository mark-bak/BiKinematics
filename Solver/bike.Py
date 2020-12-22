#Library imports
from dijkstar import Graph, find_path
import numpy as np
import scipy as sp
from scipy.optimize import minimize
import math
from collections import namedtuple
import json
import matplotlib
import matplotlib.pyplot as plt

#Local imports
from kinematic_solver import Kinematic_Solver

class Bike():
    def __init__(self,data):

        self.points = {}
        self.links = {}
        self.kinematic_loop_points = []
        self.end_eff_points = []
        self.kinematic_solver = None

        self.solution = {}

        #initialise internal variables
        self.parse_input_data(data)
        self.find_kinematic_loop()
        self.find_end_eff_points()
        self.add_kinematic_solver()

    ## Functions to process input data
    def parse_input_data(self,data):
        """
        This fcn takes input data, and populates the self.points{} and self.links{} dictionaries with point and
        link data represented as nametdtuples
        """  
        Point = namedtuple('Point',['name','type','pos'])
        Link = namedtuple('Link',['a','b','length'])

        for name in data:
            if data[name]['object']=="Point":
                P = Point(name,data[name]['type'],np.array(data[name]['position']))
                self.points[name] = P
        for name in data: # needs new loop as all points must be created before links
            if data[name]['object']=="Link":
                a_name = data[name]['a']
                b_name = data[name]['b']
                for point_name,point in self.points.items():
                    if a_name == point_name:
                        a = point
                    if b_name == point_name:
                        b = point
                length = np.linalg.norm([b.pos-a.pos])
                L = Link(a,b,length)
                self.links[name] = L

    def find_kinematic_loop(self):
        """
        Finds the kinematic loop or linkage of the suspension in multi-bar suspension systems and adds the point names (str)
        to the list self.kinemamatic_loop_points[]
        Uses shortest path algorithm along the links between the two points of type 'ground'
        """  
        g = Graph(undirected=True)
        ground =[]
        for name in self.points: # add nodes
            g.add_node(name)
        for name,link in self.links.items(): # add links
            g.add_edge(link.a.name,link.b.name,1)
        ground = [name for name in self.points if self.points[name].type=='ground'] # this is dirty
        path = find_path(g,ground[0],ground[1])
        self.kinematic_loop_points = path.nodes
        return path

    def find_end_eff_points(self):
        """
        Populates the list of point names (str) not on the 'kinematic loop' in self.end_eff_points[]
        """
        self.end_eff_points = [name for name in self.points if not name in self.kinematic_loop_points]

    ## Solver functions - need to check how these are programmed at some point

    def add_kinematic_solver(self):
        self.kinematic_solver = Kinematic_Solver(self.points,
                                                self.links,
                                                self.kinematic_loop_points,
                                                self.end_eff_points)

    def get_suspension_motion(self,travel):
        sol = self.kinematic_solver.solve_suspension_motion(travel)
        self.solution =sol

#MISC FUNCTIONS KICKING AROUND FOR NOW
def kivy_to_bike(points,links,wheelbase_px,wheelbase_mm):
    scale = wheelbase_mm/wheelbase_px
    for p in points:
        p['pos'] = [c*scale for c in p['pos'] ]

def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

#tests
if __name__ == '__main__':

    #example import from GUI
    data = load_json("C:/Users/Mark/Documents/Programming/BiKinematics/SaveFiles/Horst_Example.json")
    b = Bike(data)

    #check cartesian and link space conversions
    print('Checking coordinate conversion:')
    c = 100*np.random.rand(4,2)
    offset=c[0,:]
    ls = b.kinematic_solver.cartesian_to_link_space(c,'loop') 
    c_check = b.kinematic_solver.link_space_to_cartesian(offset,ls)

    origin = [0,0]
    point = [1,1]
    res = b.kinematic_solver.cartesian_to_link_space([origin,point])
    if c.all() == c_check.all() and res[0]-np.pi/2<0.01 and res[1]-np.sqrt(2)<0.01:
        print('--passed--')
    else:
        print('--failed--')

    #plot example rear axle path
    b.get_suspension_motion(100)
    fig, ax = plt.subplots()
    x = b.solution['Rear_Wheel'].x
    y = b.solution['Rear_Wheel'].y
    ax.plot(x, y)
    ax.set_title('Rear Axle Path')
    plt.show()
    


