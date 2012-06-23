import kivy
kivy.require('1.0.9')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, \
        Translate, Rotate, Scale
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, \
        Translate, Rotate, Scale
from kivy.uix.treeview import TreeViewNode
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from menubar import MenuBar,MenuTreeView
from kivy.factory import Factory
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
import random
import weakref
from functools import partial
from treeviewproperties import TreeViewPropertyBoolean,TreeViewPropertyText,TreeViewPropertyLabel
from state import Saver
from statusbar import StatusBar

Builder.load_string('''#:kivy 1.0.9
<Designer>:
    canvas_area:canvas_area
    treeview:treeview
    win:win
    leftbox:leftbox
    BoxLayout:
        id:win
        orientation:'horizontal'
        BoxLayout:
            id:leftbox
            size_hint:.7,1
            orientation:'vertical'
            #MenuBar
#            MenuBar:
#                id:menubar
            #Canvas box
            FloatLayout:
                size_hint:1,.95
                id:canvas_area
                canvas:
                    Color:
                        rgb:.9,.9,.8,
                    Rectangle:
                        pos: self.x, self.y
                        size: self.width,self.top
                
        #widgets box
        BoxLayout:
            size_hint:.3,1
            ScrollView:
                TreeView:
                    id: treeview
                    size_hint_y: None
                    hide_root: True
                    height: self.minimum_height
    Label:
        color:0,0,0,1
        text:'Canvas Area'
        text_size:(300,300)
        pos: 50, 100
            ''')

class Designer(FloatLayout):
    widget = ObjectProperty(None, allownone=True)
    status_bar = ObjectProperty(None)
    canvas_area = ObjectProperty(None)
    treeview = ObjectProperty(None)
    leftbox = ObjectProperty(None)
    win = ObjectProperty(None)
    numeric_keys = ObjectProperty(None)
    boolean_keys = ObjectProperty(None)
    string_keys = ObjectProperty(None)
    remaining_keys = ObjectProperty(None)
    numeric_keys, boolean_keys, string_keys,\
         remaining_keys = ([] for i in range(4))
    saved_nodes = ObjectProperty(None)
    saved_nodes = []
    widget_list = {}
    exclude_list = ["VideoPlayer", \
"VideoPlayerVolume", "VideoPlayerPlayPause", \
"VideoPlayerProgressBar"]
    #Get any widgets in kivy.uix directory
    for cls in Factory.classes:
        if cls in exclude_list:
            continue
        module_string = str(Factory.classes[cls]['module'])
        # If module is from current projects uix directory(user defined widgets)
        # or 'kivy.uix' (kivy defined widgets)
        if module_string.startswith(('uix', 'kivy.uix')):
            widget_list[cls]=str(Factory.classes[cls]['module'])
            Factory.register(cls, module=widget_list[cls])

    def __init__(self, **kwargs):
        super(Designer, self).__init__(**kwargs)
        #This following variable updates to True when ctrl is pressed
        self.ctrl_pressed = False
        
        main_menu = MenuBar(pos_hint = {'x':0,'top':1}, \
                            canvas_area = self.canvas_area, size_hint = (.70,None),height = 15)
        self.add_widget(main_menu)
        #Initialize the keyboard and set up handlers for key press and release
        self.canvas_area._keyboard = Window.request_keyboard(self._keyboard_closed,self)
        self.canvas_area._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.canvas_area._keyboard.bind(on_key_up = self._on_keyboard_up)
        # Setup canvas for highlighting
        with self.canvas.after:
            self.gcolor = Color(1, 1, 0, .25)
            PushMatrix()
            self.gtranslate = Translate(0, 0, 0)
            self.grotate = Rotate(0, 0, 0, 1)
            self.gscale = Scale(1.)
            self.grect = Rectangle(size=(0, 0))
            PopMatrix()
        # Instantiate Statusbar
        self.status_bar = StatusBar(size_hint = (1,.05))
        self.leftbox.add_widget(self.status_bar)
        
    def _keyboard_closed(self):
        '''Default keyboard closer necessary for initializing a keyboard'''
        self.canvas_area._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self.canvas_area._keyboard = None
    
    def _on_keyboard_down(self,keyboard,keycode,*largs):
        '''If 'ctrl' button is pressed, it sets the corresponding
        boolean True'''
        modifiers =  keycode[1]
        if modifiers == 'ctrl':
            self.ctrl_pressed = True
        
    def _on_keyboard_up(self,keyboard,keycode,*largs):
        ''' If 'ctrl' key is released, it makes the corresponding boolean
        go False'''
        modifiers = keycode[1]
        if modifiers == 'ctrl':
            self.ctrl_pressed = False
        
    def build(self):
        '''Builds the widget_menu for the first time, and this
        function is never called again. While building all the widget
        nodes are saved in a list called  self.saved_nodes.
        In future drawing of the widget menu, this list is used'''
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
                self.status_bar.print_status(err.message)
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
            node.bind(is_selected = self.add_new_widget)
            self.treeview.add_node(node)
            self.saved_nodes.append(node)
        
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
        return self

    def add_new_widget(self, instance, value, index=-1, *l):
        '''This function is called whenever a new widget needs to be added
        on to the canvas_area. It creates the widget and binds it with drag and
        show_properties functions'''
        if instance.is_selected:
            class_name = instance.text
            factory_caller = getattr(Factory, class_name)
            new_widget = factory_caller(size_hint=(0.2, 0.2),\
 pos=self.canvas_area.pos)
            '''If the new_widget is a Layout, we need to handle it a bit differently'''
            if isinstance(new_widget, Layout):
                with new_widget.canvas:
                    Color(0.5, 0.5, 0.5, .5)
                    Rectangle(pos = new_widget.pos, size = new_widget.size)
                new_widget.bind(pos = self.redraw_canvas,size = self.redraw_canvas)
            new_widget.bind(on_touch_move = self.drag)
            new_widget.bind(on_touch_down = self.show_properties)
            ''' If a layout element is selected and then a widget is added 
            to it, then it should be added to the selected layout
            instead of canvas_area '''
            if self.widget:
                if isinstance(self.widget,Layout):
                    self.widget.add_widget(new_widget)
                else:
                    self.canvas_area.add_widget(new_widget)
            else:
                self.canvas_area.add_widget(new_widget)
            instance.is_selected = False
    
    def redraw_canvas(self,widget,*kwargs):
        ''' This function redraws the canvas of 'Layout' widgets whenever they are
        moved or resized so that it is easy to recognize them in the canvas_area.
        As the 'Layout' widgets themselves dont have a representation.'''
        widget.canvas.clear()
        with widget.canvas:
             Color(0.5, 0.5, 0.5, .5)
             Rectangle(pos = widget.pos, size = widget.size)
    
    def drag(self, widget, touch):
        ''' This function moves the widget in the canvas_area when it is 
        dragged (on_touch_move of the widget is called)'''
        if self.widget == widget:
            '''The above check is done so that only the selected widget
            which is stored in "self.widget" is moved on drag.'''
            widget.center = touch.pos

    #def on_touch_down(self,touch):
        #TODo : There's a bug when you try to select a layout after you
        # add a widget. 
        
    def show_properties(self, widget, touch):
        '''This function is called whenever an added widget is selected
        in the canvas area. It draws the widget properties bar
        on the right, and sets up a highlighting area around the
        selected widget'''
        #Cleaning up old treeview selections
        node = self.treeview.selected_node
        self.treeview.toggle_node(node)
        #If ctrl is pressed and widget is selected we need to
        #select widget's parent 
        if self.ctrl_pressed:
            #We don't want to select parents of 1 degree widgets
            if widget.parent is not self.canvas_area:
                self.widget = widget.parent
            else:
                self.widget = widget
        else:
            self.widget = widget
        #shortening self.widget to widget as it gets used repeatedly
        widget = self.widget
        self.status_bar.print_status("Focussed on %s"%(str(widget)), t=6)
        treeview = self.treeview
        #Clearing out existing treeview
        temp = list(treeview.iterate_all_nodes())
        for node in temp:
            treeview.remove_node(node)
        self.numeric_keys, self.boolean_keys, self.string_keys,\
         self.remaining_keys = ([] for i in range(4))

        '''Adding a back button'''
        treeview.height = 30
        node = TreeViewLabel(text="< BACK TO ADD MORE WIDGETS", \
color=[1, 1, 0, 1], bold=True)
        node.bind(is_selected=self.build_menu)
        node.bind(is_selected = self.clear_selection)
        #Is this the right way to call 2 functions from a property change?
        treeview.add_node(node)
        
        '''If the widget is a layout, we need to provide
        an option to add more widgets to this layout'''
        if isinstance(widget,Layout):
            treeview.height = 30
            node = TreeViewLabel(text="Add widgets to this Layout", \
    color=[.4, 1, 0, 1])
            node.bind(is_selected=self.build_menu)
            treeview.add_node(node)
            
        '''Adding a delete button'''
        node = TreeViewLabel(text= "Delete this widget",\
 color=[1, 0, 0, 1])
        node.bind(is_selected=self.delete_item)
        treeview.add_node(node)
        treeview.height = 25
        wk_widget = weakref.ref(widget)
        keys = widget.properties().keys()
        #Here we sort out the keys into different types
        keys.sort()
        for key in keys:
            if isinstance(widget.property(key), NumericProperty):
                self.numeric_keys.append(key)
            elif isinstance(widget.property(key), StringProperty):
                self.string_keys.append(key)
            elif isinstance(widget.property(key), BooleanProperty):
                self.boolean_keys.append(key)
            elif isinstance(widget.property(key), AliasProperty):
                value = getattr(widget, key)
                if type(value) in (unicode, str):
                    self.string_keys.append(key)
                elif type(value) in (int, float):
                    self.numeric_keys.append(key)
                else:
                    self.remaining_keys.append(key)
            else:
                self.remaining_keys.append(key)

        wk_widget = weakref.ref(widget)

        # Adding all the Boolean keys
        if self.boolean_keys:
            node = TreeViewLabel(text="Boolean properties", \
                                 bold = True, color=[.25, .5, .6, 1])
            treeview.add_node(node)
            for key in self.boolean_keys:
                node = TreeViewPropertyBoolean(key=key, widget_ref=wk_widget)
                node.toggle.bind(state=partial(self.save_properties, \
                                               widget, key))
                treeview.add_node(node)

        #Adding all the Numeric keys
        if self.numeric_keys:
            node = TreeViewLabel(text="Numeric properties", \
    bold = True, color=[.25, .5, .6, 1])
            treeview.add_node(node)
            for key in self.numeric_keys:
                node = TreeViewPropertyText(key=key, \
                                                widget_ref=wk_widget)
                node.textbox.bind(text=partial(self.save_properties,\
     widget, key))
                treeview.add_node(node)

        #Adding all String keys
        if self.string_keys:
            node = TreeViewLabel(text="String properties", \
    bold = True, color=[.25, .5, .6, 1])
            treeview.add_node(node)
            for key in self.string_keys:
                node = TreeViewPropertyText(key=key, \
                                                widget_ref=wk_widget)
                node.textbox.bind(text=partial(self.save_properties,\
     widget, key))
                treeview.add_node(node)
        
        #Adding the remaining keys
        if self.remaining_keys:
            node = TreeViewLabel(text="Other properties", \
    bold = True, color=[.25, .5, .6, 1])
            treeview.add_node(node)
            for key in self.remaining_keys:
                node = TreeViewPropertyText(key=key, \
                                                widget_ref=wk_widget)
                node.textbox.bind(text=partial(self.save_properties,\
     widget, key))
                treeview.add_node(node)
        
        #Setting up highlighting of the selected widget
        Clock.schedule_interval(self.highlight_at, 0)

    def delete_item(self, instance, *largs):
        if instance.is_selected:
            #canvas_area = self.canvas_area
            parent = self.widget.parent
            parent.remove_widget(self.widget)
            self.build_menu(True)
            self.clear_selection(True)
            
    def clear_selection(self,*kwargs):
        '''This function takes away the highlight 
        and also nullifies the self.widget'''
        self.widget = None
        #We have to stop highlighing
        Clock.unschedule(self.highlight_at)
        self.grect.size = (0, 0)

    def highlight_at(self, *largs):
        gr = self.grect
        widget = self.widget
        # determine rotation
        a = Vector(1, 0)
        b = Vector(widget.to_window(*widget.to_parent(0, 0)))
        c = Vector(widget.to_window(*widget.to_parent(1, 0))) - b
        angle = -a.angle(c)

        # determine scale
        scale = c.length()

        # apply transform
        gr.size = widget.size
        self.gtranslate.xy = Vector(widget.to_window(*widget.pos))
        self.grotate.angle = angle
        self.gscale.scale = scale

    def save_properties(self, widget, key, instance, value):
        prop = widget.property(key)
        self.status_bar.print_status(repr(prop))

        if key in self.numeric_keys:
            try:
                setattr(widget, key, float(instance.text))
            except:
                self.status_bar.print_status("[Numeric] This value isn't supported", 1)
        if key in self.string_keys:
            try:
                setattr(widget, key, instance.text)
            except:
                self.status_bar.print_status("[String] This value isn't supported", 1)
        if key in self.boolean_keys:
            try:
                if instance.state == 'down':
                    setattr(widget, key, True)
                if instance.state == 'normal':
                    setattr(widget, key, False)
            except:
                self.status_bar.print_status("[Boolean] This value couldn't be saved")

    def build_menu(self, instance, *largs):
        '''This is a general purpose function that builds the
            main menu at anytime when it called with a True value.
            It uses the list self.saved_nodes to
            draw the main widget menu'''
        check = False
        try:
            check = instance.is_selected
        except:
            pass
        if check or instance:
            treeview = self.treeview
            #Copy all current nodes in a temp list
            temp = list(treeview.iterate_all_nodes())
            #Delete them.
            for node in temp:
                treeview.remove_node(node)
            for node in self.saved_nodes:
                treeview.add_node(node)
        
    #Factory.register("MenuBar", MenuBar)
    


class DesignerApp(App):

    tool = ObjectProperty(None)

    def build(self):
        self.tool = Designer()
        self.tool.build()
        return self.tool

if __name__ in ('__android__', '__main__'):
    DesignerApp().run()