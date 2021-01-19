
#Custom Imports
#pylint: disable=import-error
from KivyWidgets.links import Link,LinkData

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty

#Kivy Language Tools
from kivy.lang.builder import Builder

Builder.load_file("KivyWidgets\\components.kv")

#Shock is basicaly the same as a link - however have created seperate object for clarity and also in
#case more functionality needed later
class Shock(Link):
    Colour_Picker = ObjectProperty(None)
    pass

class ShockData(LinkData):
    pass