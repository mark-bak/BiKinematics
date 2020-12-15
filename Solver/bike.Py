from dijkstar import Graph, find_path
import numpy as np
import scipy as sp
from scipy.optimize import minimize
import math

##Todo - Really clean up all the data structures

def kivy_to_bike(points,links,wheelbase_px,wheelbase_mm):
    scale = wheelbase_mm/wheelbase_px
    for p in points:
        p['pos'] = [c*scale for c in p['pos'] ]



class Bike():
    def __init__(self,points,links,wheelbase):
        self.links = links
        self.points = points
        self.wheelbase = wheelbase
        self.loop_points = []
        self.loop_point_names = [] #comparing dicts doesn't work :(
        self.end_eff_points = []
        self.end_eff_point_names =[] #comparing dicts doesn't work :(
        self.end_eff_posns = []

        #functions to run at init
        self.find_kinematic_loop()
        self.find_end_effs()

    def find_kinematic_loop(self):
        g = Graph(undirected=True)
        ground =[]
        for p in self.points: # add nodes
            g.add_node(p['name'])
        for link in self.links: # add links
            g.add_edge(link['a'],link['b'],1)
        ground = [p['name'] for p in self.points if p['type']=='ground'] # this is dirty
        path = find_path(g,ground[0],ground[1])
        self.loop_point_names = path.nodes
        self.loop_points = self.name_to_points(path.nodes)

    def find_end_effs(self):
        #this function is horrible and i need a big rethink of how data is stored in this Bike class
        if not self.loop_points:
            print('run find_kinematic_loop first')
            return None
        #find_kinematic_loop should have already been run - add check for this
        for link in self.links:
            a = link['a']
            b = link['b']
            if not a in self.loop_point_names and not a in self.end_eff_point_names:
                self.end_eff_point_names.append(a)
                self.end_eff_points.append(self.name_to_points(a))
                self.end_eff_posns.append(self.loop_point_names.index(b))
            if not b in self.loop_point_names and not b in self.end_eff_point_names:
                self.end_eff_point_names.append(b)
                self.end_eff_points.append(self.name_to_points(b))
                self.end_eff_posns.append(self.loop_point_names.index(a)) 

    def solve_kinematic_loop(self,loop_ls):
        mid = int(loop_ls.shape[0]/2)
        x = loop_ls[1:mid-1] #angles to be found by optimiser
        geo = np.hstack([loop_ls[0],loop_ls[mid-1:]])
        res = sp.optimize.minimize(self.constraint_eqn,x,geo)
        #option here for verbose solver stuf maybe
        x_sol = res.x
        sol = loop_ls
        sol[1:mid-1] = x_sol
        return sol

    def constraint_eqn(self,x,args):
        geo = args
        n = len(x)+len(args)
        q = int(n/2)
        theta = np.hstack([geo[0],x,geo[q-len(x)-1]])
        ctheta = np.cos(theta)
        stheta = np.sin(theta)
        thetas = np.vstack([ctheta,stheta])
        L = args[q-len(x):]
        u = np.matmul(thetas,L.transpose())
        res = round(np.linalg.norm(u),3)
        return res

    def calculate_end_eff_posns(self,loop_cart,end_eff_points_ls):
        for eepls in end_eff_points_ls:
            #need to put offset link in here then converts
            cart = link_space_to_cartesian()
        return 

    def find_input_angle_range(self,travel,loop_points,end_eff_points):
        angle_range = [0,0]
        offset = loop_points[0,:]
        pls = cartesian_to_link_space(loop_points[0,:],loop_points[1:,:]+loop_points[0,:])
        eepls = []
        for eep in end_eff_points:
            eepls.append(cartesian_to_link_space([0,0],eep))
        angle_range[0] = pls[0]
        sol_ls = self.solve_kinematic_loop(pls)
        sol_cart = link_space_to_cartesian(sol_ls,offset)

        return angle_range

    def solve_leverage_ratio(self,travel):
        #find angle for required travel
        lp = np.array([list(p['pos']) for p in self.loop_points],dtype=float) # vector of points in form [[x1,y1],[x2,y2],...,[xn,yn]]
        eep = np.array([list(p['pos']) for p in self.end_eff_points],dtype=float)
        print(lp)
        self.find_input_angle_range(travel,lp,eep)

    def name_to_points(self,name_list):
        ret=[]
        if type(name_list) != list:
            name_list = list([name_list]) #lol
        for point_name in name_list:
            for p in self.points:
                if p['name'] == point_name:
                    ret.append(p)
        return ret

#Functions
def cartesian_to_link_space(orign,cart_vector):
    diff = np.diff(np.vstack([orign,cart_vector]),axis=0) #bit of a bodge to get difference betweeen last and first elements as well
    Theta_0 = np.arctan2(diff[:,1],diff[:,0]) #vector of angles [th1,th2,...,thn]
    L_0 = np.linalg.norm(diff,ord = 2,axis=1) #vector of lengths [L1,L2,...,Ln]
    v = np.concatenate([Theta_0,L_0]) #return vector of form [th1,...,thn,L1,...,Ln]
    return v

def link_space_to_cartesian(link_space_vector,offset):
    n = link_space_vector.shape[0]
    v = np.zeros((int(n/2),2)) #vector of form vector of points in form [[x1,y1],[x2,y2],...,[xn,yn]]
    v[0,:] = np.array([0,0]) + offset #first point is origin of loop
    for i in range(0,v.shape[0]-1):
        Lcos = link_space_vector[int(n/2)+i]*np.cos(link_space_vector[i])
        Lsin = link_space_vector[int(n/2)+i]*np.sin(link_space_vector[i])
        v[i+1,:] = v[i,:] + [Lcos,Lsin] #go round kinematic loop to find cartesian coords
    return v

#tests
if __name__ == '__main__':
    #check cartesian and link space conversions
    print('Checking coordinate conversion:')
    c = np.random.rand(10,2)
    offset=c[0,:]
    l_s = cartesian_to_link_space(c[0,:],c[1:,:]+c[0,:]) 
    c_check = link_space_to_cartesian(l_s,offset)

    origin = [0,0]
    point = [1,1]
    res = cartesian_to_link_space(origin,point)
    if c.all() == c_check.all() and res[0]-np.pi/2<0.01 and res[1]-np.sqrt(2)<0.01:
        print('--passed--')
    else:
        print('--failed--')


