#Library imports
import os
import csv
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
from kinematic_solver_scipy_min import Kinematic_Solver_Scipy_Min

class Bike():
    def __init__(self,data):

        self.points = {}
        self.links = {}
        self.kinematic_loop_points = []
        self.end_eff_points = []
        
        self.kinematic_solver = None #Added later in add_kinematic_solver

        self.solution = {}

        #Initialise internal variables
        self.parse_input_data(data)
        self.find_kinematic_loop()
        self.find_end_eff_points()

        #Currently adds a solver that uses Scipy minimisation fcns to numerically solve
        #linkage constraint eqns, however more solvers will likely need to be created for
        #single pivots, and maybe a freudenstein eqn 4-bar solver could also be made
        default_Solver = Kinematic_Solver_Scipy_Min(self.points,
                                                    self.links,
                                                    self.kinematic_loop_points,
                                                    self.end_eff_points)
        self.set_kinematic_solver(default_Solver)
        
    ##Functions to process input data
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
        Finds the kinematic loop or linkage of the suspension and adds the point names (str format)
        to the list self.kinemamatic_loop_points[]
        Uses shortest path algorithm to find path between two points of type 'ground', along the minimum
        number of links
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

    def set_kinematic_solver(self,Solver):
        """
        Adds the kinematic solver which can be used to calculate suspension motion
        """
        self.kinematic_solver = Solver

    def get_suspension_motion(self,travel,name):
        """
        Runs the kinematic solver class attached to this instance, and returns the suspension motion
        throughout the specified travel in self.solution
        """
        sol = self.kinematic_solver.solve_suspension_motion(travel)
        self.solution[name] = sol

    ##Data i/o functions
    def save_solution_csv(self,solution_name):
        """
        Not implemented yet - fcn to save solution data as a csv
        """
        filename = solution_name + '.csv'
        with open(filename, 'w', newline ='') as f:
            writer = csv.writer(f, delimiter=',',
            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for point_name in self.solution[solution_name]:
                writer.writerow([point_name+'_x',self.solution[solution_name][point_name].x])
                writer.writerow([point_name+'_y',self.solution[solution_name][point_name].y])



#MISC FUNCTIONS KICKING AROUND FOR NOW
def kivy_to_bike(points,links,wheelbase_px,wheelbase_mm):
    scale = wheelbase_mm/wheelbase_px
    for p in points:
        p['pos'] = [c*scale for c in p['pos'] ]

def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

##Tests - requires Horst_Example.json - need to distribute this in the Github
if __name__ == '__main__':

    #example import from GUI
    data = load_json("Horst_Example.json")
    b = Bike(data)

    #check cartesian and link space conversions
    print('Checking coordinate conversion:')
    c = 100*np.random.rand(4,2)
    offset=c[0,:]
    ls = b.kinematic_solver.cartesian_to_link_space(c,'loop') 
    c_check = b.kinematic_solver.link_space_to_cartesian(offset,ls,'loop')

    origin = [0,0]
    point = [1,1]
    res = b.kinematic_solver.cartesian_to_link_space([origin,point])
    if c.all() == c_check.all() and res[0]-np.pi/2<0.01 and res[1]-np.sqrt(2)<0.01:
        print('--passed--')
    else:
        print('--failed--')

    #plot example rear axle path
    b.get_suspension_motion(100,'test')
    fig, ax = plt.subplots()
    x = b.solution['test']['Rear_Wheel'].x
    y = b.solution['test']['Rear_Wheel'].y
    ax.plot(x, y)
    ax.set_title('Rear Axle Path')
    #plt.show()
    b.save_solution_csv('test')
    


