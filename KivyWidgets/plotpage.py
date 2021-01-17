#General imports
import csv
import numpy as np

#Kivy Layouts
from kivy.uix.floatlayout import FloatLayout

#Kivy Language
#pylint: disable=no-name-in-module
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

#Kivy Custom Widgets
#pylint: disable=import-error
from KivyWidgets.dialogs import LoadDialog
from KivyWidgets.mainpage import ThemePopup
from KivyWidgets.mainpage import TopbarButton

#Kivy matplotlib
import matplotlib
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg




Builder.load_file("KivyWidgets/plotpage.kv")

class PlotPage(FloatLayout): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.results = {}
        self.x_plot_data = []
        self.y_plot_data = []
        self.fig,self.ax = self.create_plot()
    
    results_filename = StringProperty('Click to add results file')
    x_data_name = StringProperty('No Data')
    y_data_name = StringProperty('No Data')

    def create_plot(self):
        fig,ax = plt.subplots()
        self.ids['graph_frame'].add_widget(FigureCanvasKivyAgg(plt.gcf()))
        return fig,ax
 
    def dismiss_popup(self):
        self._popup.dismiss()

    def open_results_dialog(self):
        content = LoadDialog(load=self.load_results, cancel=self.dismiss_popup,directory = "\\Results")
        self._popup = ThemePopup(title="Load results", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def load_results(self,path,selection):
        filename = selection[-1]

        self.results_filename = filename.replace(path+"\\","")

        with open(filename) as f:
            reader = csv.reader(f, delimiter=',',quotechar='|')
            for row in reader:
                self.results[row[0]] = np.array(row[1:],dtype = 'float')
        self.dismiss_popup()
    
    def show_data_dropdown(self,parent,axis):
        dropdown = DropDown()
        for result_name in self.results:
            btn = TopbarButton(text=result_name,
                               size_hint_y=None,
                               height = 25)
            dropdown.add_widget(btn)
            btn.bind(on_release=lambda btn: dropdown.dismiss())
            btn.bind(on_release=lambda btn: self.select_data(btn.text,axis))

        dropdown.open(parent)

    def select_data(self,selection,axis):
        if axis == 'x':
            self.x_data_name = selection
            self.x_plot_data = self.results[selection]
        if axis == 'y':
            self.y_data_name = selection
            self.y_plot_data = self.results[selection]


    def plot(self):
        try:
            self.ax.clear()
            self.ax.plot(self.x_plot_data, self.y_plot_data)
            self.fig.canvas.draw()
            self.ax.autoscale()
        except:
            pass

        



