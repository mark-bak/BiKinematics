#Standard Imports
import json

#Custom Widget Imports
#pylint: disable=import-error
from KivyWidgets.links import Link
from KivyWidgets.links import LinkData
from KivyWidgets.components import Shock
from KivyWidgets.components import ShockData
from KivyWidgets.components import Cog
from KivyWidgets.components import Chain
from KivyWidgets.components import Wheel
from KivyWidgets.dialogs import LoadDialog
from KivyWidgets.dialogs import SaveDialog
from KivyWidgets.dialogs import PointDialog
from KivyWidgets.dialogs import SimulateDialog
from KivyWidgets.points import Point
from KivyWidgets.points import PointData
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

#Custom imports
from bikinematicsolver.bike import Bike

#Kivy Layouts
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image

#Kivy Properties
#pylint: disable=no-name-in-module
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty

#Kivy Language Tools
from kivy.lang.builder import Builder
from kivy.core.window import Window

Builder.load_file("KivyWidgets\\mainpage.kv")

class MainPage(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #Window resize binding
        Window.bind(on_resize=self.on_window_resize)
        Window.maximize()
        #Sizes of some GUI elements - edit in .kv file
        self.sidebar_width = self.ids['sidebar'].width
        self.topbar_height = self.ids['topbar'].height
        #self.info_text_height = self.ids['current_mode'].height

        #Set dropdown widgets
        self.LoadDropDown = LoadDropDown(mp = self)
        self.AddGeoDropDown = AddGeoDropDown(mp = self)
        self.DeleteDropDown = DeleteDropDown(mp = self)
        self.AnalDropDown = AnalDropDown(mp = self)

    ##Kivy properties
    #Info text
    mode = StringProperty('Main')
    info = StringProperty()

    #Link creation list
    link_points = ListProperty()

    #Image filename
    image_file = StringProperty()

    #Unit and window scaling
    px_to_mm = NumericProperty(1)
    cur_width = NumericProperty(Window.width)
    cur_height = NumericProperty(Window.height)

    #Sizes of some GUI elements - edit in .kv file
    sidebar_width = NumericProperty()
    topbar_height = NumericProperty()
    info_text_height = NumericProperty()

    #Dropdown widgets
    LoadDropDown = ObjectProperty()
    AddGeoDropDown = ObjectProperty()
    DeleteDropDown = ObjectProperty()
    AnalDropDown = ObjectProperty()

    ##General methods
    def dismiss_popup(self):
        """
        Dismisses current popup
        """
        self.mode = 'Main'
        self._popup.dismiss()

    def clear_all(self):
        """
        Clears all geometry widgets
        """
        for wid in self.walk():
            if isinstance(wid,Point):
                self.delete_point(wid)
            if isinstance(wid,Link):
                self.delete_link(wid)
            if isinstance(wid,Chain):
                self.remove_widget(wid)
            if isinstance(wid,Cog):
                self.remove_widget(wid)
            if isinstance(wid,Wheel):
                self.remove_widget(wid)

    def on_window_resize(self, window, width, height): 
        """
        Resizes geo elements on window resize
        """
        old_width = self.cur_width
        old_height = self.cur_height

        height_offset = 0
        #Rescale all point widgets:
        self.rescale_geo(old_width,
                         width,
                         old_height,
                         height,
                         height_offset)
        
        #Update stored 'old' value of window width
        self.cur_width = width
        self.cur_height = height

    def change_mode(self,mode,info):
        self.mode = mode
        self.info = info

    def rescale_geo(self, old_width, new_width, old_height, new_height, height_offset=0):
        """
        Walks all points and rescales according to window changes
        """
        #Gets size of image frame before resize
        old_imf_width = old_width - self.sidebar_width 
        old_imf_height = old_height - self.topbar_height

        #Gets size of image frame after resize
        new_imf_width = new_width - self.sidebar_width 
        new_imf_height = new_height - self.topbar_height

        #Walk points and rescale
        for w in self.walk():
            if isinstance(w,Point):
                w.scale_with_window(old_imf_width,
                                    new_imf_width,
                                    old_imf_height,
                                    new_imf_height,
                                    height_offset)
        
        #Update scaling factor from pixels to mm
        self.update_px_mm_conversion()

    def update_px_mm_conversion(self):
        """
        Modifies the scaling factor self.px_to_mm, giving ratio of wheelbase in pixels to actual bike wheelbase in mm

        Sets self.px_to_mm to 0 if the front and rear wheels are not defined in geometry, and 0 if bad data is entered in wheelbase GUI input
        """
        #Find which points are the front and rear wheels - (Maybe store these as an instance variable this looks kind of slow)
        fw = None
        rw = None
        for wid in self.children:
            if isinstance(wid,Point):
                if wid.point_type == 'front_wheel':
                    fw = wid
                if wid.point_type == 'rear_wheel':
                    rw = wid
        if fw != None and rw != None:
            #If front and rear wheel exist, calculate scaling factor
            wbase_px = abs(fw.x-rw.x)
            try:
                wbase_mm = float(self.ids['params_list'].wheelbase)
            except:
                wbase_mm = 0 #If user has entered some funky stuf in text box, set wbase_mm (and tf px_to_mm) to zero
            self.px_to_mm = wbase_mm / wbase_px
            #print(self.px_to_mm)
        else:
            #If front and rear wheel not specified, set scaling to 0
            self.px_to_mm = 0
        
    def goto_plot(self):
        """
        Displays plotpage
        """  
        self.parent.manager.transition.direction = 'right'
        self.parent.manager.current = 'Plot' #lol what a mess this line is
    
    def show_dropdown(self,dropdown,parent):
        """
        Opens dropdown, attaching to parent widget
        """
        dropdown.open(parent)

    ##User input methods
    def on_touch_down(self,touch):
        """
        Custom touch behaviour
        """
        if self.mode == 'Add_Point' and self.collide_point(touch.x,touch.y): #Add points if in Add_Point mode
            self.open_point_dialog(touch)
        return super(MainPage,self).on_touch_down(touch) #Do standard touch behaviour

    ##Load methods
    def open_load_dialog(self):
        """
        Opens a LoadDialog, with selection passed to self.load_bike_data
        """
        content = LoadDialog(load=self.load_bike_data, cancel=self.dismiss_popup,directory = "\\SaveFiles")
        self._popup = ThemePopup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
   
    def load_bike_data(self, path, selection):
        """
        Load bike savedata in json format, and convert to GUI geometry widgets
        """
        filename = selection[-1]
        with open(filename) as f:
            data = json.load(f)

            ##Geometry  Loading
            #Add all Points
            for point_name,point in data['points'].items():
                self.add_point(point_name,point['type'],point['pos'])

            #Add links and shocks between the points - needs new loop as all points must be created before links      
            for link_name,link in data['links'].items():
                a_ref = link['a']
                b_ref = link['b']
                for w in self.walk(): #Find points corresponding to ref string
                    if isinstance(w,Point):
                        if w.name == a_ref:
                            a = w
                        if w.name == b_ref:
                            b = w
                if link_name == data['shock']:
                    self.add_shock(a=a,b=b)
                else:
                    self.add_link(a=a,b=b) #Create link with corresponding points

            #Add shock

            ##Parameter Loading
            self.load_param(data,'wheelbase')
            self.load_param(data,'chainring_teeth')
            self.load_param(data,'cassette_teeth')
            self.load_param(data,'wheel_size')
            self.load_param(data,'cog_height')

            self.ids['point_colour'].color = data['params']['point_colour']
            self.ids['shock_colour'].color = data['params']['shock_colour']
            self.ids['link_colour'].color = data['params']['link_colour']
            #Rescaling
            new_width = Window.width
            new_height = Window.height
            old_width = data['params']['window_width']
            old_height = data['params']['window_height']
            self.rescale_geo(old_width,
                             new_width,
                             old_height, 
                             new_height)
            #Image Loading
            if data['params']['image_file']:
                self.load_image('',data['params']['image_file'])

    def load_param(self,data,param_name):
        """
        Attempts to load parameter from file, and won't crash the program if it can't :)
        """
        try:
            self.ids[param_name].text = data['params'][param_name]
        except:
            pass
        
    #Save methods
    def open_save_dialog(self):
        """
        Opens a SaveDialog, with selection passed to self.save_bike_data
        """
        content = SaveDialog(save = self.save_bike_data,cancel = self.dismiss_popup)
        self._popup = ThemePopup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def save_bike_data(self,filename,path):
        """
        Saves a json at path\\filename.json, with info describing the geometry objects and constants needed to define the bike.
        """
        #Filename parsing
        filename = filename.replace(path+"\\","") #Remove path from filename
        ind = filename.find('.') #Find whether there is file ext
        if ind != -1: 
            #Remove file ext if present
            filename = filename[0:ind]
        filename = "{}\\{}.json".format(path,filename) #Put in path with .json extension
        
        #Save bike data
        save_data = self.create_bike_data(sf=1)
        with open(filename,'w') as f:
            json.dump(save_data,f,indent=2)

    def create_bike_data(self,sf):
        """
        Creates simple json file with info describing the geometry objects and constants needed to define the bike.
        This file is typically 'keyed' by the name of the widget/point/link

        The geometry positions will be scaled by sf (defualt value 1 - no scaling).
        """

        points = {}
        links = {}
        #data = {}

        ##Add geometry object/widget data
        for w in self.walk():
            if isinstance(w,Point):
                point_data={'name':w.name,'type':w.point_type,'pos':tuple([w.x*sf,w.y*sf])}
                points[w.name]= point_data
            if isinstance(w,Link):
                link_data={'name':w.name,'a':w.a.name,'b':w.b.name}
                links[w.name]= link_data
            if isinstance(w,Shock):
                shock = w.name
        
        ##Add other parameters - these also end up getting passed to solver and some not used but guess its no big deal
        values = [['wheelbase',             self.ids['wheelbase'].text              ],
                  ['chainring_teeth',       self.ids['chainring_teeth'].text        ],
                  ['cassette_teeth',        self.ids['cassette_teeth'].text         ],
                  ['wheel_size',            self.ids['wheel_size'].text             ],
                  ['window_width',          self.cur_width                          ],
                  ['window_height',         self.cur_height                         ],
                  ['image_file',            self.image_file                         ],
                  ['point_colour',          self.ids['point_colour'].color          ],
                  ['link_colour',           self.ids['link_colour'].color           ],
                  ['shock_colour',          self.ids['shock_colour'].color          ],
                  ['p2mm',                  self.px_to_mm                           ],
                  ['cog_height',            self.ids['cog_height'].text             ]]

        params = {}
        for par in values:
            params[par[0]] = par[1]

        data = {'points':points,
                'links':links,
                'shock':shock,
                'params':params}   

        return data

    ##Image methods
    def open_image_dialog(self):
        """
        Opens a LoadDialog, with selection passed to self.load_image
        """
        content = LoadDialog(load=self.load_image, cancel=self.dismiss_popup,directory = "\\ImageFiles")
        self._popup = ThemePopup(title="Load file", content=content,
                    size_hint=(0.9, 0.9))
        self._popup.open()

    def load_image(self,path,filename):
        """
        Adds a widget image to the image frame bit of GUI, from filename
        """
        if isinstance(filename,list):
            filename = filename[-1]
        self.clear_image()
        self.image_file = filename
        self.ids['image_frame'].add_widget(Image(source=filename,
                                                 pos=self.ids['image_frame'].pos,
                                                 allow_stretch=True))

    def clear_image(self):
        """
        Clears image from image frame
        """
        for child in self.ids['image_frame'].children:
            self.ids['image_frame'].remove_widget(child)

    ##Add point methods
    def open_point_dialog(self,touch):
        """
        Opens a point dialog for point parameter entry, at click/touch position
        """
        content = PointDialog(add=self.add_point,cancel = self.dismiss_popup,touch = touch)
        self._popup = ThemePopup(title="Add Point", content=content,
                            size_hint=(None,None),size = (400,150),
                            pos_hint={  'x': touch.x / self.width, 
                                        'y': touch.y / self.height}) 
        self._popup.open()

    def add_point(self,name,typ,pos):
        """
        Adds Point wdiget to app, with name type and position, name,typ,pos respectively
        """
        #Create and add point widget
        new_point = Point(name = name,point_type = typ,pos = pos,colour_picker=self.ids['point_colour'])
        #Add circles and stuff to certain points
        if new_point.point_type == 'bottom_bracket':
            self.add_widget(Cog(centrepoint = new_point,diameter_ref = self.ids['chainring_teeth'],mp = self))
        if new_point.point_type == 'rear_wheel':
            self.add_widget(Cog(centrepoint = new_point,diameter_ref = self.ids['cassette_teeth'],mp = self))
            self.add_widget(Wheel(centrepoint = new_point,diameter_ref = self.ids['wheel_size'],mp = self))
        if new_point.point_type == 'front_wheel':
            self.add_widget(Wheel(centrepoint = new_point,diameter_ref = self.ids['wheel_size'],mp = self))

        #Link to data display at sidebar
        new_point_data = PointData(point = new_point,name=name,point_type=typ)
        new_point.point_data = new_point_data       
        self.add_widget(new_point)

        #Add sidebar info widgets
        self.ids['points_list'].add_widget(new_point_data)
        self.dismiss_popup()
        #Update app info text
        self.info = 'Point \'{}\' added'.format(new_point.name)
        self.update_px_mm_conversion() #Run in case new wheel point added

    def delete_point(self,point):
        """
        Removes Point widget, point, from the app, and associated sidebar info widget
        """
        self.ids['points_list'].remove_widget(point.point_data)
        self.remove_widget(point)
        self.info = 'Point \'{}\' removed'.format(point.name)
        self.mode = 'Main'
        self.update_px_mm_conversion()

    ##Add link methods
    def on_link_points(self,instance,value):
        """
        Called when the self.link_points list is modified. If this list now has 2 unique points, creates a link between them and exits link creating mode
        """
        objs = value
        self.info = '{} of 2 points selected'.format(str(len(self.link_points)))
        #Check if points are unique, if duplicates, pop first from list
        if len(objs)>1 and objs[0]==objs[1]:
            objs.pop(0) 
        #Add link between points in list
        if len(objs)>1:
            a = objs[0]
            b = objs[1]
            if self.mode == 'Add_Link':
                self.add_link(a,b)
            if self.mode == 'Add_Shock':
                self.add_shock(a,b)
            self.link_points.clear()
            self.mode = 'Main'

    def add_link(self,a,b):
        """
        Adds Link widget to app, between Point widgets a and b
        """
        #Create link and add
        new_link = Link(a = a, b = b, colour_picker = self.ids['link_colour'])
        new_link_data = LinkData(link = new_link, mp=self)
        new_link.link_data = new_link_data
        self.add_widget(new_link)
        #Add sidebar info widget
        self.ids['links_list'].add_widget(new_link_data)
        #Info text update
        self.info = 'Link \'{}\' added'.format(new_link.name)

    def add_shock(self,a,b):
        #Create shock and add
        new_shock = Shock(a = a, b = b, colour_picker = self.ids['shock_colour'])
        new_shock_data = ShockData(link = new_shock, mp=self)
        new_shock.link_data = new_shock_data
        self.add_widget(new_shock)
        #Add sidebar info widget
        self.ids['links_list'].add_widget(new_shock_data)
        #Info text update
        self.info = 'Link \'{}\' added'.format(new_shock.name)

    def delete_link(self,link):
        """
        Deletes Link widget and associated sidebar info widget
        """
        self.ids['links_list'].remove_widget(link.link_data)
        self.remove_widget(link)
        self.mode = 'Main'

    #Chainline
    def show_chain(self):
        cog_list =[]
        for wid in self.walk():
            if isinstance(wid,Cog):
                cog_list.append(wid)
        if len(cog_list)==2:
            print('here')
            self.add_widget(Chain(cassette = cog_list[0],chainring = cog_list[1]))
            print('h2')
        else:
            self.info = 'Need chainring and cassette to add a chain!'

    ##Simulate methods
    def open_sim_dialog(self):
        """
        Opens a dialog where simulation params can be sepcified
        """
        content = SimulateDialog(simulate=self.simulate,cancel = self.dismiss_popup)
        self._popup = ThemePopup(title="Simulate", content=content,
                            size_hint=(None,None),size = (400,150)) 
        self._popup.open()

    def simulate(self,filename,desired_travel):
        """
        Simulates geometry on screen for desired_travel (mm) - outputs results in \\Results\\filename.csv
        """
        #Setup sim params

        desired_travel = float(desired_travel)
        sim_data = self.create_bike_data(sf = self.px_to_mm)
        b = Bike(sim_data)
        sol_name = 'Single_Sim'
        #Simulate
        b.get_suspension_motion(desired_travel,sol_name) #Base linkage movement
        b.calculate_suspension_characteristics(sol_name) #Derived susp characteristics
        b.save_solution_csv(sol_name,filename) #Save

        #Go to plotpage and view results:
        self.parent.manager.get_screen('Plot').children[0].load_results('Results\\',filename) #Potentially the worst line of code I have written so far
        self.goto_plot()

        self.dismiss_popup()
        self.info = 'Simulation: {} complete'.format(filename)

##Other widgets used for UI - see .kv for formatting
#Dropdown style classes
class LoadDropDown(DropDown):
    mp = ObjectProperty(None)  

class AddGeoDropDown(DropDown):
    mp = ObjectProperty(None) 

class DeleteDropDown(DropDown):
    mp = ObjectProperty(None)

class AnalDropDown(DropDown):
    mp = ObjectProperty(None)

#Custom popup hacky thing - see .kv
class ThemePopup(Popup):
    bg_color = ListProperty([0,0,0,1])

#Button theme
class TopbarButton(Button):
    pass