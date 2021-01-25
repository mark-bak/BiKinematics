from collections import namedtuple

#Named tuple used in solutions for easier syntax
Pos_Result = namedtuple('Pos_Result',['x','y'])
#Geo data
Point = namedtuple('Point',['name','type','pos'])
Link = namedtuple('Link',['a','b','length'])
