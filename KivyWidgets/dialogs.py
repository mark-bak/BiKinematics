#Standard Imports
import os
import re

#Kivy Layouts
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
#Kivy Language Tools
from kivy.lang.builder import Builder

Builder.load_file("KivyWidgets\\dialogs.kv")

class LoadDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    directory = StringProperty()
    def get_dir(self):
        return os.getcwd()+self.directory

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

class SimulateDialog(BoxLayout):
    simulate = ObjectProperty(None)
    cancel = ObjectProperty(None)
    #layout defined in .kv file
    pass

#Super useful class I nicked from Kivy docs
class FloatInput(TextInput):
    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)