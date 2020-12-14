from dijkstar import Graph, find_path
import numpy as np
import scipy as sp
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

    def find_kinematic_loop(self):
        g = Graph(undirected=True)
        ground =[]
        for p in self.points: # add nodes
            g.add_node(p['name'])
        for link in self.links: # add links
            g.add_edge(link['a'],link['b'],1)
        ground = [p['name'] for p in self.points if p['type']=='ground'] # this is dirty
        path = find_path(g,ground[0],ground[1])
        self.loop_points = []
        for point_name in path.nodes:
            for p in self.points:
                if p['name'] == point_name:
                    self.loop_points.append(p)
        return path

    def solve_kinematic_loop(self):
        n_points = len(self.loop_points)
        lp =np.array([list(p['pos']) for p in self.loop_points],dtype=float)
        #z = np.zeros(lp.shape[0]*lp.shape[1])
        diff = np.diff(np.vstack([lp,lp[0,:]]),axis=0)
        Theta_0 = np.arctan2(diff[:,1],diff[:,0])
        L_0 = np.linalg.norm(diff,ord = 2,axis=1)
        v = np.concatenate([Theta_0,L_0])
        x = v[1:n_points-1] #angles to be found by optimiser
        geo = np.hstack([v[0],v[n_points-1:]])
        check = self.constraint_eqn(x,geo)
        print(check)
        
    def constraint_eqn(self,x,args):
        geo = args
        n = len(x)+len(args)
        q = int((n/2))
        theta = np.hstack([geo[0],x,geo[q-len(x)-1]])
        ctheta = np.cos(theta)
        stheta = np.sin(theta)
        thetastack = np.vstack([ctheta,stheta])
        L = args[q-len(x):]
        u = np.matmul(thetas,L.transpose())
        print(u)
        print(theta)
        print(L)
        res = round(np.linalg.norm(u),3)
        return res

    def solve_leverage_ratio(self,travel):
        path = self.find_kinematic_loop()
        self.solve_kinematic_loop()