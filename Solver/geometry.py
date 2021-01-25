import numpy as np
#pylint: disable = import-error
from Solver.dtypes import Pos_Result  

def find_intersection(a1,a2,b1,b2):
    """
    Finds intersection of lines a and b, described by points a1,a2,b1,b2
    Accepts vector input of shape (2,N)
    Returns (x_int,y_int)
    """
    #Eqn first line
    m_a = np.subtract( a2.y , a1.y ) / np.subtract( a2.x , a1.x ) 
    c_a = np.subtract( a1.y,  m_a * a1.x ) 
    #Eqn second line
    m_b = np.subtract( b2.y , b1.y ) / np.subtract( b2.x , b1.x ) 
    c_b = np.subtract( b1.y, m_b * b1.x )
    #Intersction point
    x0 = np.subtract( c_b , c_a ) / np.subtract( m_a, m_b )
    y0 = np.add( m_b * x0  , c_b ) 

    ic = Pos_Result(x0,y0)      
    return ic

def tangent_eqn(cen,r1,r2):
    delta_r = r2-r1
    z = np.add( np.power(cen[0],2) , np.power(cen[1],2))
    d = np.sqrt( np.subtract( z , np.power(delta_r,2) ) )
    
    a = np.add( cen[0]*delta_r, cen[1]*d  ) / z
    b = np.subtract( cen[1]*delta_r, cen[0]*d  ) / z
    c = r1
    ret = [a,b,c]
    return ret

def find_common_circle_tangent(cen1,r1,cen2,r2):
    tan_lines = []
    for i in [-1,1]:
        for j in [-1,1]: 
            cen = np.subtract(cen2 , cen1)
            #print(cen)
            tan_lines.append(tangent_eqn(cen, r1 * i, r2 * j))
    for line in tan_lines:
        s = np.add( line[0] * cen1[0] , line[1] * cen1[1])
        line[2] = np.subtract( line[2] , s )
    return tan_lines

def find_circle_tangent_intersection(cen,tangent_line):
    """
    Finds the intersection point of a circle and a line TANGENT!!!!!!!!!!!!!!!!!!!!!! to the circle
    """
    line = tangent_line[:]
    s = np.add( line[0] * cen[0] , line[1] * cen[1])
    line[2] = np.add( line[2] , s )
    
    z = np.add( np.power(line[0],2) , np.power(line[1],2) )
    x0 = -(line[0] * line[2]) / z + cen[0]
    y0 = -(line[1] * line[2] ) / z + cen[1]

    ic = Pos_Result(x0,y0)
    return ic