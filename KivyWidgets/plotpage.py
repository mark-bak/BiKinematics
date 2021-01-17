
#Kivy Layouts
from kivy.uix.floatlayout import FloatLayout

#Kivy Language
#pylint: disable=no-name-in-module
from kivy.lang.builder import Builder
from kivy.properties import StringProperty

#Kivy Custom Widgets
from KivyWidgets.dialogs import LoadDialog
from KivyWidgets.mainpage import ThemePopup

#Kivy matplotlib
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from matplotlib import pyplot as plt

Builder.load_file("KivyWidgets/plotpage.kv")

class PlotPage(FloatLayout): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.fig, self.ax = self.create_plot()
    
    results_file = StringProperty('Click to add results file')

    def create_plot(self):
        fig,ax = plt.subplots()
        fig1 = FigureCanvasKivyAgg(plt.gcf())
        self.ids['graph_frame'].add_widget(fig1)
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
        filename = filename.replace(path+"\\","") #remove path from filename

        self.results_file = filename
        self.dismiss_popup()
        pass