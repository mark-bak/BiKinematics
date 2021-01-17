#Standard Imports
import os

#Kivy Layouts
from kivy.uix.boxlayout import BoxLayout

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty

#Kivy Language Tools
from kivy.lang.builder import Builder

Builder.load_file("KivyWidgets/dialogs.kv")

class LoadDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    def get_dir(self):
        return os.getcwd()+'\\SaveFiles'

class SaveDialog(BoxLayout):
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)
    def get_dir(self):
        return os.getcwd()+'\\SaveFiles'

class PointDialog(BoxLayout):
    add = ObjectProperty(None)
    cancel = ObjectProperty(None)
    touch = ObjectProperty(None)
    #layout defined in .kv file
    pass
