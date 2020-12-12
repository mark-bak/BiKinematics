
#Kivy Layouts
from kivy.uix.floatlayout import FloatLayout
#Kivy Language
from kivy.lang.builder import Builder

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from matplotlib import pyplot as plt

Builder.load_file("KivyWidgets/plotpage.kv")

class PlotPage(FloatLayout): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.plot()
    
    def plot(self):
        fig,ax = plt.subplots()
        fig1 = FigureCanvasKivyAgg(plt.gcf())
        self.ids['graph_frame'].add_widget(fig1)