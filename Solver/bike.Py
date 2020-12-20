from dijkstar import Graph, find_path
import numpy as np
import scipy as sp
from scipy.optimize import minimize
import math
from collections import namedtuple
import json

class Bike():
    def __init__(self,data):

        self.points = {}
        self.links = {}
        self.kinematic_loop_points = []
        self.end_eff_points = []

        #initialise internal variables
        self.parse_input_data(data)
        self.find_kinematic_loop()
        self.find_end_eff_points()

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

    def get_solution_space_vectors(self):
        """
        Comment later
        """
        klp = np.array([self.points[name].pos for name in self.kinematic_loop_points],dtype=float) # vector of points in form [[x1,y1],[x2,y2],...,[xn,yn]]
        eep = np.array([self.points[name].pos for name in self.end_eff_points],dtype=float)

        klp_off = klp[0,:] 
        klp_ss = cartesian_to_link_space(klp,'loop')
        
        eep_posn=[]
        eep_ss =np.zeros(eep.shape[0]*2)
        for end_eff_index in range(len(self.end_eff_points)):

            attach_point_index = self.find_end_eff_attach_point(self.end_eff_points[end_eff_index])
            eep_posn.append(attach_point_index)

            Th,L = cartesian_to_link_space([klp[attach_point_index],eep[end_eff_index]])
            eep_ss[end_eff_index] = Th
            eep_ss[eep.shape[0]+end_eff_index] = L

        return klp_off,klp_ss,eep_posn,eep_ss

    def find_end_eff_attach_point(self,end_eff_point):
        for link in self.links.values():
            if link.a.name == end_eff_point:
                return self.kinematic_loop_points.index(link.b.name)
            if link.b.name == end_eff_point:
                return self.kinematic_loop_points.index(link.a.name)

    def solve_kinematic_loop(self,loop_ls):
        """
        expects vector of form vector of form [th1,...,thn,L1,...,Ln]
        """
        mid = int(loop_ls.shape[0]/2)
        x = loop_ls[1:mid-1] #angles to be found by optimiser (this defo works for 4-bar need to test higher dims...)
        geo = np.vstack([loop_ls[0],loop_ls[mid-1:]])
        res = sp.optimize.minimize(self.constraint_eqn,x,geo)

        #option here for verbose solver stuf maybe
        x_sol = np.vstack(res.x)
        sol = loop_ls
        sol[1:mid-1] = x_sol
        return sol

    def constraint_eqn(self,x,args):
        geo = args
        n = len(x)+len(args)
        q = int(n/2)
        theta = np.hstack([geo[0],x,geo[q-1]])
        ctheta = np.cos(theta)
        stheta = np.sin(theta)
        thetas = np.vstack([ctheta,stheta])
        L = args[q-len(x):]
        u = np.matmul(thetas,L)
        err = np.linalg.norm(u)
        #print(err)
        return err

    def solve_leverage_ratio(self,travel):
        #find angle for required travel
        pass


#Functions
def cartesian_to_link_space(v,*params):
    """
    Takes a (nx2) vector of points in form v = [[x1,y1],[x2,y2],...,[xn,yn]], and converts to generalised coord: angles from horizontal Theta,
    and magnitdues L, measured from  successive points/joints. Return is (2(n-1)x1) vector of form [th1,th2,...,th(n-1),L1,L2,...,L(n-1)]
    If 'loop' is passed as a parameter, the generalised coord to return from the last point in v to the first is also included, returning a (2nx1) vector
    of form [th1,th2,...,thn,L1,L2,...,Ln]
    """

    if 'loop' in params:
        v = np.concatenate([v,[v[0,:]]])

    diff = np.diff(v,axis=0)
    Theta = np.vstack(np.arctan2(diff[:,1],diff[:,0])) #vector of angles [th1,th2,...,thn]
    L = np.vstack(np.linalg.norm(diff,ord = 2,axis=1)) #vector of lengths [L1,L2,...,Ln]
    ls = np.vstack([Theta,L])
    return ls

def link_space_to_cartesian(offset,ls):
    """
    Takes a (nx2) vector of points in form v = [[x1,y1],[x2,y2],...,[xn,yn]], and converts to generalised coord: angles from horizontal Theta,
    and magnitdues L, measured from  successive points/joints. Return is (2nx1) vector of form [th1,th2,...,thn,L1,L2,...,Ln]
    """
    N = int(ls.shape[0]/2)
    Theta = ls[0:N]
    L = ls[N:]
    n = Theta.shape[0]
    v = np.zeros((n,2)) #vector of form vector of points in form [[x1,y1],[x2,y2],...,[xn,yn]]
    v[0,:] = np.array([0,0]) + offset #first point is origin of loop
    for i in range(0,v.shape[0]-1):
        Lcos = L[i]*np.cos(Theta[i])
        Lsin = L[i]*np.sin(Theta[i])
        v[i+1,:] = v[i,:] + np.hstack([Lcos,Lsin]) #loop to find cartesian coords
    return v


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
    #check cartesian and link space conversions
    print('Checking coordinate conversion:')
    c = 10*np.random.rand(4,2)
    offset=c[0,:]
    ls = cartesian_to_link_space(c,'loop') 
    c_check = link_space_to_cartesian(offset,ls)

    origin = [0,0]
    point = [1,1]
    res = cartesian_to_link_space([origin,point])
    if c.all() == c_check.all() and res[0]-np.pi/2<0.01 and res[1]-np.sqrt(2)<0.01:
        print('--passed--')
    else:
        print('--failed--')

    #example import from GUI
    data = load_json("C:/Users/Mark/Documents/Programming/BiKinematics/SaveFiles/Horst_Example.json")
    b = Bike(data)
    path = b.find_kinematic_loop()
    klp_off,klp_ss,eep_posn,eep_ss = b.get_solution_space_vectors()
    print(klp_ss)
    print(path)
    print(klp_off)
    print(eep_posn)
    print(eep_ss)

    klp_ss[0] = 3
    sol = b.solve_kinematic_loop(klp_ss)
    print(sol)

