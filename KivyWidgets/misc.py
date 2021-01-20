#Standard imports 
import re

#Kivy imports
from kivy.uix.textinput import TextInput
from kivy.lang.builder import Builder

Builder.load_file("KivyWidgets/misc.kv")

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