
#Custom Imports
#pylint: disable=import-error
from KivyWidgets.links import Link,LinkData

#Kivy Language Tools
from kivy.lang.builder import Builder

Builder.load_file("KivyWidgets\\components.kv")

#Shock is basicaly the same as a link - however have created seperate object for clarity and also in
#case more functionality needed later
class Shock(Link):
    pass

class ShockData(LinkData):
    pass