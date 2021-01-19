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


 
#Local imports
# pylint: disable = import-error
if __name__ == '__main__':
    import matplotlib
    import matplotlib.pyplot as plt

    from kinematic_solver_scipy_min import Kinematic_Solver_Scipy_Min,Pos_Result
else:
    from Solver.kinematic_solver_scipy_min import Kinematic_Solver_Scipy_Min,Pos_Result

class Bike():
    def __init__(self,data):
        
        #Required bike geo values
        self.points = {}
        self.links = {}
        self.kinematic_loop_points = []
        self.end_eff_points = []
        self.static_points = []
        
        self.kinematic_solver = None #Added later in set_kinematic_solver

        self.solution = {}

        #Initialise internal variables
        self.parse_input_data(data)
        self.find_kinematic_loop()
        self.find_static_points()
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

    def find_static_points(self):
        """
        Populates the list of point names (str) that do not move relative to frame in self.end_static_points[]
        """   
        self.static_points = [name for name in self.points if self.points[name].type == "front_wheel" or self.points[name].type == "shock_frame"]

    def find_end_eff_points(self):
        """
        Populates the list of point names (str) that are attached to kinematic loop in self.end_eff_points[]
        """
        self.end_eff_points = [name for name in self.points if not name in self.kinematic_loop_points and not name in self.static_points]

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
        return sol

    def calculate_suspension_characteristics(self,sol_name):
        """
        Calculates derived suspension characteristics such as leverage ratio, from a solution result, sol_name.

        Directly modifies self.solution[sol_name]
        """

        ##Static Points
        for point_name in self.static_points: 
            x = np.ones(np.size(list(self.solution[sol_name].values())[0].x)) * self.points[point_name].pos[0]
            y = np.ones(np.size(list(self.solution[sol_name].values())[0].y)) * self.points[point_name].pos[1]
            self.solution[sol_name][point_name] = Pos_Result(x,y)

        ##Travels and leverage ratio

        #Find points of interest
        for name in self.points:
            if self.points[name].type == 'rear_wheel':
                rw_name = name 
            if self.points[name].type == 'shock_linkage':
                sl_name = name
            if self.points[name].type == 'shock_frame':
                sf_name = name
        
        #Maths
        Vertical_Travel = self.solution[sol_name][rw_name].y - np.ones(np.size(self.solution[sol_name][rw_name].y)) * self.solution[sol_name][rw_name].y[0]
        shock_delta_x = np.subtract(self.solution[sol_name][sl_name].x, self.solution[sol_name][sf_name].x)
        shock_delta_y = np.subtract(self.solution[sol_name][sl_name].y, self.solution[sol_name][sf_name].y)
        Shock_Length = np.linalg.norm(np.vstack([shock_delta_x,shock_delta_y]),axis=0)
        #Shock_Length = np.abs(Shock_Length - np.ones(np.size(Shock_Length)) * Shock_Length[0])
        
        #Numerical derivative (shoddy rn, do a better one!!)
        delta_shock_length = np.diff(Shock_Length)
        delta_vertical_travel = np.diff(Vertical_Travel)             
        Leverage_Ratio = np.abs(np.divide(delta_vertical_travel, delta_shock_length))
        Leverage_Ratio = np.hstack([Leverage_Ratio,Leverage_Ratio[-1]]) 
        
        #Derived suspension characeristics
        self.solution[sol_name]['Vertical_Travel'] = Vertical_Travel
        self.solution[sol_name]['Shock_length'] = Shock_Length
        self.solution[sol_name]['LeverageRatio'] = Leverage_Ratio

    ##Data i/o functions
    def save_solution_csv(self,solution_name,filename):
        """
        Fcn to save solution data, solution_name, as a csv called filename
        """
        #Ensure correct filetype
        ind = filename.find('.')
        if ind != -1:
            filename = filename[0:ind]
        filename = "Results\\{}.csv".format(filename)

        #Save data
        with open(filename, 'w', newline ='') as f:
            writer = csv.writer(f, delimiter=',',
            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for point_name in self.solution[solution_name]:
                if isinstance(self.solution[solution_name][point_name],Pos_Result):
                    writer.writerow([point_name+'_x']+list(self.solution[solution_name][point_name].x))
                    writer.writerow([point_name+'_y']+list(self.solution[solution_name][point_name].y))
                else:
                    writer.writerow([point_name]+list(self.solution[solution_name][point_name]))
                    pass

##Tests - requires Horst_Example.json - need to distribute this in the Github
def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

if __name__ == '__main__':

    #example import from GUI
    data = load_json("VitusSommetGeo.json")
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
    b.calculate_suspension_characteristics('test')
    fig, ax = plt.subplots()
    x = b.solution['test']['Rear_Wheel'].x
    y = b.solution['test']['Rear_Wheel'].y
    ax.plot(x, y)
    ax.set_title('Rear Axle Path')
    #plt.show()
    b.save_solution_csv('test','test_file')
    


