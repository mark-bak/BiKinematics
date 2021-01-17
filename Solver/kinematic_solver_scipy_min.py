#Library imports
from dijkstar import Graph, find_path
import numpy as np
import scipy as sp
from scipy.optimize import minimize
import math
from collections import namedtuple
import json


class Kinematic_Solver_Scipy_Min():
    def __init__(self,points,links,kin_loop_points,end_eff_points):
        """
        Copy over relevant variables from Bike representation
        """
        self.points = points
        self.links = links
        self.kinematic_loop_points = kin_loop_points
        self.end_eff_points = end_eff_points

    def get_solution_space_vectors(self):
        """
        Returns vectors in solution space form, ready for solving. This form is the following:

        1st return: klp_off - a point of form [x,y], denoting the offset of the linkage loop origin from the
        origin used in the cartesian representation of the bike (currently the bottom left screen pixel)

        2nd return: klp_ss - a vector containing the angle and length generalised coords of the linkage of the format:
        [th12,th23,...,th(n-1)(n),th(n)1 , L12,L23,...,L(n-1)(n),L(n)1], i.e the magnitude and angle of the vectors
        between the points of the loop.

        Note - These are ordered with respect to self.kinematic_loop_points list, where in the notation used
        in this fcn description the first entry (self.kinematic_loop_points[0]) will be the name of the point 
        with coords [x1,y1]

        3rd return: eep_ss - a vector containing the angle and length offset of a particular end effector from
        linkage point given in eep_posn. This vector has form [th,L]

        4th return: eep_posn - the index of the linkage point that the end effector is offset from

        Note - These are ordered with respect to self.end_eff_points list, where in the notation used
        in this fcn description the first entry (self.end_eff_points[0]) will be the name of the end effector 
        with offset given by eep_ss[0] from linkage point self.kinematic_loop_points(eep_posn[0]) 

        """
        klp = np.array([self.points[name].pos for name in self.kinematic_loop_points],dtype=float) #vector of points in form [[x1,y1],[x2,y2],...,[xn,yn]]
        eep = np.array([self.points[name].pos for name in self.end_eff_points],dtype=float) #vector of points in form [[x1,y1],[x2,y2],...,[xn,yn]]

        #Convert loop 
        klp_off = klp[0,:] 
        klp_ss = self.cartesian_to_link_space(klp,'loop')
        
        #Convert end effectors
        eep_posn=[]
        eep_ss =np.zeros(eep.shape[0]*2) # Converting (n x 2) [[x1,y1]...[xn,yn]] shape to [th1...thn,L1...Ln] (2n x 1) shape

        for end_eff_index in range(len(self.end_eff_points)): #Loop through end eff points and find attachment point and offset            
            #Find attach point
            attach_point_index = self.find_end_eff_attach_point(self.end_eff_points[end_eff_index])
            #Find offset from attach point to end effector
            Th,L = self.cartesian_to_link_space([klp[attach_point_index],eep[end_eff_index]])

            #Store in expected format
            eep_posn.append(attach_point_index)
            eep_ss[end_eff_index] = Th
            eep_ss[eep.shape[0]+end_eff_index] = L # Converting (n x 2) [[x1,y1]...[xn,yn]] shape to [th1...thn,L1...Ln] (2n x 1)  shape

        return klp_off,klp_ss,eep_ss,eep_posn

    def find_end_eff_attach_point(self,end_eff_point):
        """
        Returns index of linkage point attachment (via link) for given end_eff point. If end effector is attached to multiple linkage points,
        this will return the first it comes across. Needs error checking written if no attachment at all.
        """
        for link in self.links.values():
            if link.a.name == end_eff_point:
                return self.kinematic_loop_points.index(link.b.name)
            if link.b.name == end_eff_point:
                return self.kinematic_loop_points.index(link.a.name)

    def solve_kinematic_loop(self,loop_ls):
        """
        Expects (2n x 1) input vector of form v = [th1,...,th(n),L1,...,L(n)]. Typical usage is to set the input angle,
        th1 to desired value, then pass to this function to find new solution vector for this input angle.

        Returns (2n x 1) solution vector s = [th1,...,th(n),L1,...,L(n)] satisfying the linkage constraint equation
        """
        #Process input data for solver
        mid = int(loop_ls.shape[0]/2)
        x = loop_ls[1:mid-1] #Constrained coordinates to be found by optimiser (this defo works for 4-bar need to test higher dims...)
        geo = np.vstack([loop_ls[0],loop_ls[mid-1:]]) #Constant generalised coords (Link lengths, ground angle)

        #Solve by minimising error in linkage constraint equation
        res = sp.optimize.minimize(self.constraint_eqn,
                                   x,
                                   geo) #This solves by minimsing error in the linkage loop equation

        #Return solution in expected format
        x_sol = np.vstack(res.x)
        sol = loop_ls
        sol[1:mid-1] = x_sol
        return sol

    def solution_to_cartesian(self,klp_off,klp_sol,eep_ss,eep_posn):
        """
        Takes klp_off,klp_sol,eep_ss,eep_posn as described in self.get_solution_space_vectors, and returns cartesian coords of form:
        [[xl1,yl1],...,[xl(nl),yl(nl)],[xe1,ye1],...,[xe(ne),ye(ne)]], where nl and ne denote number of kinematic loop and end effector
        points respectively
        """
        #Linkage loop points can be directly converted
        klp_v = self.link_space_to_cartesian(klp_off,
                                             klp_sol,
                                             'loop')
        
        #End effector points need dealt with 
        mid = int(eep_ss.shape[0]/2)
        eep_v = np.zeros((mid,2)) #Reshape (2n x 1)-> (n x 2)
        for i in range(mid): #Loop through ee generalised coords and get position in cartesian space
            pos = self.link_space_to_cartesian(klp_v[eep_posn[i],:], #Offset is attach point
                                               np.vstack([eep_ss[i],eep_ss[mid+i]])) #Gets representation in form [th(n),L(n)]
            eep_v[i,:]=pos[1] #Don't need attachemnt coords, only end effector coords

        #Return expected format
        return np.vstack([klp_v,eep_v])

    def constraint_eqn(self,x,args):
        """
        Finds vector u = [u_x,u_y], given by u_x = sum(lcos(th)), and u_y = sum(lsin(th)) by some neat matrix multiplication
        Then finds magnitude of this vector and returns it -> this signifies the error in the linkage constraint
        """
        #Data setup
        geo = args
        n = len(x)+len(args)
        q = int(n/2)
        theta = np.vstack([geo[0],np.reshape(x,(len(x),1)),geo[1:q-len(x)]])
        theta = theta.transpose()

        #Constraint eqn
        ctheta = np.cos(theta)
        stheta = np.sin(theta)
        thetas = np.vstack([ctheta,stheta])
        L = args[q-len(x):]
        u = np.matmul(thetas,L)
        #Error
        err = np.linalg.norm(u)

        return err

    def solve_suspension_motion(self,travel):
        """
        Solves the suspension motion for a desired travel in PIXELS AT THE MOMENT THIS NEEDS TO CHANGE,
        This is the one you want to run and it calls all the other functions as needed - probably a better stylistic way to represent this??

        Returns a solution as a dictionary of NamedTuples with x and y data, for example to get x data for point with name Name use solution[Name].x
        This returns a N long vector/list/np_thingy where N is the number of solver steps
        """

        #Convert data into link space coordinates for solving
        klp_off,klp_ss,eep_ss,eep_posn = self.get_solution_space_vectors()
        
        #Find the input angles in form [current input angle,......, angle required to acheive desired simulation travel] 
        input_angles = self.find_input_angle_range(travel,klp_off,klp_ss,eep_ss,eep_posn)
        #print([input_angles[0],input_angles[-1]])

        point_results= np.zeros(( len(self.kinematic_loop_points)+len(self.end_eff_points) , 2 , input_angles.shape[0])) #Result vector
        for i in range(len(input_angles)): #Solve the linkage at each angle of the input link, and convert to cartesian (see note)
            klp_ss[0]=input_angles[i]
            klp_sol = self.solve_kinematic_loop(klp_ss)
            point_results[:,:,i] = self.solution_to_cartesian(klp_off,klp_sol,eep_ss,eep_posn) # (this is probably slow in here - can move out later if performance issues)

        #Convert data to solution format
        points_list = self.kinematic_loop_points + self.end_eff_points
        Pos_Result = namedtuple('Pos_Result',['x','y'])
        solution = {}
        for i in range(point_results.shape[0]):
            name = points_list[i]
            solution[name] = Pos_Result(point_results[i,0,:],point_results[i,1,:])
        return solution

    def find_input_angle_range(self,travel,klp_off,klp_ss,eep_ss,eep_posn):
        """
        Takes desired simulation travel and solution space vectors, and returns a range of input angles from [th0,...,tht], where th0 is the starting angle
        at zero suspension travel, and tht is the angle of the input link that gives the desired simulation travel. The number of angles in the 
        range is currently hardcoded at 100, but I will change this at some point.

        Currently no error checking for unachievable angles - needs implemented likely based off whether optimisation target < 1e-2 or something similar  
        """

        #Find rear wheel initial vertical position
        for name,point in self.points.items():
            if point.type == 'rear_wheel':
                rear_wheel_name = name
                rear_wheel_init_y = point.pos[1]
        r_w_ind = self.end_eff_points.index(rear_wheel_name) + len(self.kinematic_loop_points) #List index of rear wheel point coordinates

        #Setup up solver to find angle that minimises error between desired y position (at specified travel), and y position of rear wheel
        #found from linkage solver
        desired_y = rear_wheel_init_y+travel
        th_in_0 = float(klp_ss[0])
        res = sp.optimize.minimize(self.travel_find_eqn,
                                   th_in_0,
                                   [desired_y, r_w_ind,klp_off, klp_ss,eep_ss, eep_posn],
                                   method = 'Nelder-Mead',
                                   options={'disp':True})
        
        #Create return vector from initial and final angles
        th_in_end = res.x
        input_angles = np.linspace(th_in_0,th_in_end,num=100) #Unhardcode this number at some point
        return input_angles
        
    def travel_find_eqn(self,x,args):
        """
        Solves the linkage equation with the input solution space vectors, and returns the (absolute!) error between the rear wheel y position and the desired.

        Maybe need to look at the fcn input to make more clear, but last time it tried it didn't work so well with the sp.optimize.minimize this is passed to
        """
        #This is a bit ugly for now, maybe find a neater way to pass through the variables??
        desired_y = args[0]
        r_w_ind = args[1]
        klp_off = args[2]
        klp_ss = args[3]
        eep_ss = args[4]
        eep_posn = args[5]

        klp_ss[0]= x #The optimisation variable is the input angle of the linkage
        klp_sol = self.solve_kinematic_loop(klp_ss) #Solve linkage with this angle

        #Convert to cartesian and find error between desired and actual rear wheel y position
        sol_cartesian = self.solution_to_cartesian(klp_off,klp_sol,eep_ss,eep_posn)
        y = sol_cartesian[r_w_ind,1]
        err = np.abs(desired_y-y)
        #print(err)
        return err

    def cartesian_to_link_space(self,v,*params):
        """
        Takes a (n x 2) vector of points in form v = [[x1,y1],[x2,y2],...,[x(n),y(n)]], and converts to generalised coord: angles from horizontal Theta,
        and magnitdues L, measured from  successive points/joints. Return is (2(n-1) x 1) vector of form [th12,th23,...,th(n-1)(n),L12,L23,...,L(n-1)(n)]
        If 'loop' is passed as a parameter, the generalised coord to return from the last point in v to the first is also included, returning a (2n x 1) vector
        of form [th12,th23,...,th(n-1)(n),th(n)1,L12,L23,...,L(n-1)(n),L(n)1]
        """

        #Add first point to end of list again if 'loop'is specified
        if 'loop' in params:
            v = np.concatenate([v,[v[0,:]]])

        #Perform conversion
        diff = np.diff(v,axis=0)
        Theta = np.vstack(np.arctan2(diff[:,1],diff[:,0])) #Vector of angles [th1,th2,...,thn]
        L = np.vstack(np.linalg.norm(diff,ord = 2,axis=1)) #Vector of lengths [L1,L2,...,Ln]
        ls = np.vstack([Theta,L])
        return ls

    def link_space_to_cartesian(self,offset,ls,*params):
        """
        Takes set of link space generalised coordinates of form [th12,th23,...,th(n-1)(n),L12,L23,...,L(n-1)(n)], and an offset coordinate [x0,y0] and 
        returns cartesian coords of form [[x1,y1],[x2,y2],...,[x(n),y(n)]]. For loops use the 'loop' in *params otherwise it will return the origin of the loop
        twice - at the start and the end.
        """

        #Data sizing fun
        N = int(ls.shape[0]/2)
        Theta = ls[0:N]
        L = ls[N:]
        n = Theta.shape[0]
        #Shape return vector depending on loop or not
        if 'loop' in params:
            v = np.zeros((n,2)) #Vector of points in form [[x1,y1],[x2,y2],...,[xn,yn]]
        else:
            v = np.zeros((n+1,2)) #Vector of points in form [[x1,y1],[x2,y2],...,[xn,yn]]

        #Conversion
        v[0,:] = np.array([0,0]) + offset #First point is offset (some weird numpy stuff going on here as well :) )
        for i in range(0,v.shape[0]-1): #Loop through -> next coords are [xold,yold] + [lcos(th),Lsin(th)]
            Lcos = L[i]*np.cos(Theta[i])
            Lsin = L[i]*np.sin(Theta[i])
            v[i+1,:] = v[i,:] + np.hstack([Lcos,Lsin]) #loop to find cartesian coords
        
        return v

