from dijkstar import Graph, find_path

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
        return path

    def solve_leverage_ratio(self,travel):
        pass