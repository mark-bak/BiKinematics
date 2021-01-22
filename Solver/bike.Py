#Library imports
import os
import csv
from dijkstar import Graph, find_path
import numpy as np
import scipy as sp
from scipy.optimize import minimize
import math
import json

#Solver imports
#pylint: disable = import-error
from Solver.kinematic_solver_scipy_min import Kinematic_Solver_Scipy_Min
from Solver.dtypes import Pos_Result

class Bike():
    def __init__(self,data):
        
        #Required bike geo values
        self.points = {}
        self.links = {}
        self.shock = None
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
            if data[name]['object']=="Link" or data[name]['object']=="Shock":
                a_name = data[name]['a']
                b_name = data[name]['b']
                for point_name,point in self.points.items():
                    if a_name == point_name:
                        a = point
                    if b_name == point_name:
                        b = point
                length = np.linalg.norm([b.pos-a.pos])
                L = Link(a,b,length)
                if data[name]['object']=="Link":
                    self.links[name] = L
                if data[name]['object']=="Shock":
                    self.shock = L


    def find_kinematic_loop(self):
        """
        Finds the kinematic loop or linkage of the suspension and adds the point names (str format)
        to the list self.kinemamatic_loop_points[]
        Uses shortest path algorithm to find path between two points of type 'ground', along the minimum
        number of links
        """  
        grounds = [name for name in self.points if self.points[name].type == "front_wheel" or self.points[name].type == "ground"]

        #Create graph for shortest path
        g = Graph(undirected=True)
        for name in self.points: # add nodes
            g.add_node(name)
        for name,link in self.links.items(): # add links
            g.add_edge(link.a.name,link.b.name,1)
        
        path = None
        #Loop between grounds, and find the ones connected by links
        for i in range(len(grounds)):
            for j in range(len(grounds)):
                if i !=j and i<j:
                    try:
                        path = find_path(g,grounds[i],grounds[j]) #Fnd shortest path betweeen these two grounds - almost 100% sure this always gives kin. path 
                        path_list = path.nodes
                    except:
                        pass
        
        if path is None:
            rear_wheel_name = [name for name in self.points if self.points[name].type == "rear_wheel"]
            for i in range(len(grounds)):
                try:
                    path = find_path(g,grounds[i],rear_wheel_name[0])
                    path_list = path.nodes
                    path_list.append(grounds[i])
                    print(path_list)
                except:
                    pass

        self.kinematic_loop_points = path_list
        return path

    def find_static_points(self):
        """
        Populates the list of point names (str) that do not move relative to frame in self.end_static_points[]
        """   
        self.static_points = [name for name in self.points if self.points[name].type == "front_wheel" or self.points[name].type == "ground"]

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
        sol = self.solution[sol_name]
        size = np.size(list(sol.values())[0].x) 

        ##Static Points
        for point_name in self.static_points:
            r = self.populate_static_point(sol, size,point_name)
            self.solution[sol_name][point_name] = r
        
        ##Instant centre
        if len(self.kinematic_loop_points) < 4:
            #If single pivot - Ic is constant
            Instant_Centre = self.populate_static_point(sol,size,self.kinematic_loop_points[0])
        else:
            #4-bar soln
            a1 = sol[ self.kinematic_loop_points[0] ]
            a2 = sol[ self.kinematic_loop_points[1] ]
            b1 = sol[ self.kinematic_loop_points[-2] ]
            b2 = sol[ self.kinematic_loop_points[-1] ] 

            Instant_Centre = self.find_intersection(a1,a2,b1,b2)

        ##Derived characteristics
        #Find RW point
        rw_name = None
        for name in self.points:
            if self.points[name].type == 'rear_wheel':
                rw_name = name
        #Get zero-based wheel travel 
        if rw_name is not None:
            rw_norm = self.offset_to_zero(sol,size,rw_name)
            Vertical_Travel = rw_norm.y
            Axle_Path_X = rw_norm.x
        else:
            Vertical_Travel = np.zeros(size)
            Axle_Path_X = np.zeros(size)

        if self.shock is not None:
            #Find shock point names
            s_a_name = self.shock.a.name
            s_b_name = self.shock.b.name
            Shock_Length = self.calc_distance(sol[s_a_name] , sol[s_b_name])
            Leverage_Ratio = self.calc_derivative(Vertical_Travel,Shock_Length)
            #Add to solution
        else:
            Shock_Length = np.zeros(size)
            Leverage_Ratio = np.zers(size)

        #Populate solution
        self.solution[sol_name]['Shock Length'] = Shock_Length
        self.solution[sol_name]['Leverage Ratio'] = Leverage_Ratio
        self.solution[sol_name]['Vertical Travel'] = Vertical_Travel
        self.solution[sol_name]['Axle Path X'] = Axle_Path_X
        self.solution[sol_name]['Instant Centre'] = Instant_Centre

    def populate_static_point(self,sol,size,point_name):
        x = np.ones(size) * self.points[point_name].pos[0]
        y = np.ones(size) * self.points[point_name].pos[1]
        return Pos_Result(x,y)

    def offset_to_zero(self,sol,size,point_name):
        #Normalised  path
        y = sol[point_name].y - np.ones(size) * sol[point_name].y[0] # s - I*s[0]
        x = sol[point_name].x - np.ones(size)  * sol[point_name].x[0]
        return Pos_Result(x,y)

    def calc_distance(self,a,b):
        dx = np.subtract(a.x , b.x)
        dy = np.subtract(a.y , b.y)
        L = np.linalg.norm(np.vstack([dx,dy]),axis=0)
        return L

    def calc_derivative(self,x,y):
        dydx = np.abs(np.gradient(x, y))
        return dydx


    def find_intersection(self,a1,a2,b1,b2):
        """
        Finds intersection of lines a and b, described by points a1,a2,b1,b2
        Accepts vector input of shape (2,N)
        Returns (x_int,y_int)
        """
        #Eqn first line
        m_a = np.divide( np.subtract( a2[1] , a1[1] ), np.subtract( a2[0] , a1[0] ) )
        c_a = np.subtract( a1.y, np.multiply( m_a , a1[0]) ) 
        #Eqn second line
        m_b = np.divide( np.subtract( b2[1] , b1[1] ), np.subtract( b2[0] , b1[0] ) )
        c_b = np.subtract( b1.y, np.multiply( m_b , b1[0]) )
        #Intersction point
        x_ic = np.divide( np.subtract( c_b , c_a ) , np.subtract( m_a, m_b ) )
        y_ic = np.add( np.multiply( m_b , x_ic ) , c_b ) 

        ic = Pos_Result(x_ic,y_ic)      
        return ic

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



