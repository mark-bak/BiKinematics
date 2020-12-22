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

class Kinematic_Solver():
    def __init__(self,points,links,kin_loop_points,end_eff_points):
        self.points = points
        self.links = links
        self.kinematic_loop_points = kin_loop_points
        self.end_eff_points = end_eff_points

    def get_solution_space_vectors(self):
        """
        Comment later
        """
        klp = np.array([self.points[name].pos for name in self.kinematic_loop_points],dtype=float) # vector of points in form [[x1,y1],[x2,y2],...,[xn,yn]]
        eep = np.array([self.points[name].pos for name in self.end_eff_points],dtype=float)
        #print(np.vstack([klp,eep]))
        klp_off = klp[0,:] 
        klp_ss = self.cartesian_to_link_space(klp,'loop')
        
        eep_posn=[]
        eep_ss =np.zeros(eep.shape[0]*2)
        for end_eff_index in range(len(self.end_eff_points)):

            attach_point_index = self.find_end_eff_attach_point(self.end_eff_points[end_eff_index])
            eep_posn.append(attach_point_index)

            Th,L = self.cartesian_to_link_space([klp[attach_point_index],eep[end_eff_index]])
            eep_ss[end_eff_index] = Th
            eep_ss[eep.shape[0]+end_eff_index] = L

        return klp_off,klp_ss,eep_ss,eep_posn

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

    def solution_to_cartesian(self,klp_off,klp_sol,eep_ss,eep_posn):
        klp_v = self.link_space_to_cartesian(klp_off,klp_sol)
        
        mid = int(eep_ss.shape[0]/2)
        eep_v = np.zeros((mid,2))
        for i in range(mid):
            pos = self.link_space_to_cartesian(klp_v[eep_posn[i],:],np.vstack([eep_ss[i],0,eep_ss[mid+i],0]))# this needs fixed - maybe some options for loop or not in the 
            #ls->cart function
            eep_v[i,:]=pos[1]
        return np.vstack([klp_v,eep_v])

    def constraint_eqn(self,x,args):
        geo = args
        n = len(x)+len(args)
        q = int(n/2)
        theta = np.vstack([geo[0],np.reshape(x,(len(x),1)),geo[1:q-len(x)]])
        theta = theta.transpose()
        ctheta = np.cos(theta)
        stheta = np.sin(theta)
        thetas = np.vstack([ctheta,stheta])
        L = args[q-len(x):]
        u = np.matmul(thetas,L)
        err = np.linalg.norm(u)

        return err

    def solve_suspension_motion(self,travel):
        klp_off,klp_ss,eep_ss,eep_posn = self.get_solution_space_vectors()
        input_angles = self.find_input_angle_range(travel,klp_off,klp_ss,eep_ss,eep_posn)
        print([input_angles[0],input_angles[-1]])
        point_results= np.zeros(( len(self.kinematic_loop_points)+len(self.end_eff_points) , 2 , input_angles.shape[0]))
        for i in range(len(input_angles)):
            klp_ss[0]=input_angles[i]
            klp_sol = self.solve_kinematic_loop(klp_ss)
            point_results[:,:,i] = self.solution_to_cartesian(klp_off,klp_sol,eep_ss,eep_posn)
            #klp_ss = klp_sol

        points_list = self.kinematic_loop_points + self.end_eff_points
        Pos_Result = namedtuple('Pos_Result',['x','y'])
        solution = {}
        for i in range(point_results.shape[0]):
            name = points_list[i]
            solution[name] = Pos_Result(point_results[i,0,:],point_results[i,1,:])
        return solution

    def find_input_angle_range(self,travel,klp_off,klp_ss,eep_ss,eep_posn):

        for name,point in self.points.items():
            if point.type == 'rear_wheel':
                rear_wheel_name = name
                rear_wheel_init_y = point.pos[1]
        r_w_ind = self.end_eff_points.index(rear_wheel_name)+len(self.kinematic_loop_points)

        desired_y = rear_wheel_init_y+travel
        
        th_in_0 = float(klp_ss[0])

        res = sp.optimize.minimize(self.travel_find_eqn,th_in_0,[desired_y,r_w_ind,klp_off,klp_ss,eep_ss,eep_posn],method = 'Nelder-Mead',options={'disp':True})
        
        th_in_end = res.x
        input_angles = np.linspace(th_in_0,th_in_end,num=100)
        return input_angles
        
    def travel_find_eqn(self,x,args):
        desired_y = args[0]
        r_w_ind = args[1]
        klp_off = args[2]
        klp_ss = args[3]
        eep_ss = args[4]
        eep_posn = args[5]

        klp_ss[0]=x
        klp_sol = self.solve_kinematic_loop(klp_ss)

        sol_cartesian = self.solution_to_cartesian(klp_off,klp_sol,eep_ss,eep_posn)
        y = sol_cartesian[r_w_ind,1]
        err = np.abs(desired_y-y)
        #print(err)
        return err

    def cartesian_to_link_space(self,v,*params):
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

    def link_space_to_cartesian(self,offset,ls):
        """
        comment later
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

