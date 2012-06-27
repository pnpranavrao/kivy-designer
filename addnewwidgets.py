import kivy
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeViewNode
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from treeviewproperties import TreeViewPropertyBoolean, \
 TreeViewPropertyText,TreeViewPropertyLabel
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.lang import Builder
import weakref
from functools import partial
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, \
        Translate, Rotate, Scale
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

Builder.load_string('''#:kivy 1.0.9
<NewWidgetsMenu>:
    treeview:treeview
    TreeView:
        id: treeview
        size_hint_y: None
        hide_root: True
        height: self.minimum_height
            ''')

class NewWidgetsMenu(ScrollView):
    '''This class is responsible for :
    * Factory building a list of addable widgets and layout at startup
    * Add all these widgets in a scrollable treeview, and save a copy in 'saved_nodes'
    * Rebuild this original list whenever needed, by using 'saved_nodes', and
      adding any necessary observers
    * add_new_widget(self, *kwargs, parent = None) is an important function which instantiates
    the new widget from kwargs data, and adds it as a child to parent. If parent is None, it is
    added to Designer.canvas_Area
    
    Note : The function build_menu is not directly called by observers and is redireced
    to the Designer class where rebuild_menu calls it. This is to facilitate handling of 
    parent - rightbox's widgets properly'''
    
    exclude_list = ["VideoPlayer", \
                    "VideoPlayerVolume", "VideoPlayerPlayPause", \
                    "VideoPlayerProgressBar"]
    widget_list = {}
    treeview = ObjectProperty(None)
    saved_nodes = []
    
    #Get all widget classes in kivy.uix directory
    for cls in Factory.classes:
        if cls in exclude_list:
            continue
        module_string = str(Factory.classes[cls]['module'])
        # If module is from current projects uix directory(user defined widgets)
        # or 'kivy.uix' (kivy defined widgets)
        if module_string.startswith(('uix', 'kivy.uix')):
            widget_list[cls]=str(Factory.classes[cls]['module'])
            Factory.register(cls, module=widget_list[cls])
    
    def __init__(self, designer, **kwargs):
        '''Builds the widget_menu for the first time, and this
        function is never called again. 
        While building all the widget nodes are saved in a list called
        'saved_nodes' (without any binding) for future use'''
        
        super(NewWidgetsMenu, self).__init__(**kwargs)
        self.designer = designer
        self.canvas_area = designer.canvas_area
        self.popup = None
        
        keys=[]
        layout_keys = []
        for cls in self.widget_list:
            if cls == "Camera":
                '''This is because there seems to be some bug in Gstreamer
                when we load a camera widget and don't use it '''
                continue
            try:
                factory_caller = getattr(Factory, str(cls))
                new_widget = factory_caller()
                if isinstance(new_widget, Layout):
                    layout_keys.append(cls)
                    continue
                if isinstance(new_widget, Widget):
                    keys.append(cls)
            except Exception as err:
                pass
                #self.status_bar.print_status(err.message)
        keys.append('Camera')
        keys.sort()
        layout_keys.sort()
        
        '''Adding all the widgets to the menu'''
        node = TreeViewLabel(text= " Widgets", bold = True, \
                             color=[.25, .5, .6, 1])
        self.treeview.add_node(node)
        self.saved_nodes.append(node)
        node = None
        for key in keys:
            text = '%s' % key
            node = TreeViewLabel(text=text)
            self.saved_nodes.append(node)
            node.bind(is_selected = self.add_new_widget)
            self.treeview.add_node(node)
            
        
        '''Adding all the Layouts to the menu'''
        node = TreeViewLabel(text= "Layouts ", bold = True, \
                             color=[.25, .5, .6, 1])
        self.treeview.add_node(node)
        self.saved_nodes.append(node)
        for key in layout_keys:
            text = '%s' % key
            node = TreeViewLabel(text = text)
            node.bind(is_selected = self.add_new_widget)
            self.treeview.add_node(node)
            self.saved_nodes.append(node)
        
    def add_new_widget(self, instance, value, parent = None):
        '''This function is called whenever a new widget needs to be added
        on to the canvas_area. It can be called in two scenarios :
        * From the basic menu, where the widget needs to be added to 'canvas_area'
        * From a nested menu, where the widget needs to be added to a layout.
        It creates the widget and binds it with drag function'''
        #print "In add_new_widgets" + str(parent)
        if instance.is_selected:
            parent = parent or self.canvas_area
            if self.designer.root_name == "":
                # We dont have the root class's name.
                content = BoxLayout(orientation = 'vertical')
                textbox = TextInput(text = '')
                btn = Button(text = "Save", size_hint_y = .2)
                btn.bind(on_release = partial(self.save_popup, textbox))
                content.add_widget(textbox)
                content.add_widget(btn)
                self.popup = Popup(title='Enter root class\'s name',
                              content=content,
                              size_hint=(None, None), size=(400, 200))
                self.popup.open()
            class_name = instance.text
            factory_caller = getattr(Factory, class_name)
            new_widget = factory_caller(size_hint=(0.2, 0.2),\
                                        pos=self.canvas_area.pos)
            '''If the new_widget is a Layout, we need to handle it a bit differently'''
            if isinstance(new_widget, Layout):
                with new_widget.canvas:
                    Color(0.5, 0.5, 0.5, .5)
                    Rectangle(pos = new_widget.pos, size = new_widget.size)
                new_widget.bind(pos = self.designer.redraw_canvas,size = self.designer.redraw_canvas)
            new_widget.id = self.designer.give_id()
            new_widget.bind(on_touch_move = self.designer.drag)
            parent.add_widget(new_widget)
            # Is setting False like below allowed?
            instance.is_selected = False
    
    def save_popup(self, textbox, button):
        if self.popup:
            self.popup.dismiss()
        self.designer.root_name = textbox.text
        
    def build_menu(self, parent = None):
        '''This is a general purpose function that builds the
        main menu at anytime using self.saved_nodes
        Its main use case is to display addable widgets and 
        layouts to a selected layout in canvas_area.
        It is called from Designer.rebuild_menu() '''
        
        treeview = self.treeview
        #Copy all current nodes in a temp list
        temp = list(treeview.iterate_all_nodes())
        #Delete them.
        for node in temp:
            treeview.remove_node(node)
        
        for node in self.saved_nodes:
            node.bind(is_selected = partial(self.add_new_widget, parent = parent))
            treeview.add_node(node)


