import kivy
kivy.require('1.0.9')

import sys
import inspect
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
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
from menubar import MenuBar,MenuTreeView
from kivy.factory import Factory
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
import random
import weakref
from functools import partial
from state import Saver
from statusbar import StatusBar
from addnewwidgets import NewWidgetsMenu
from showproperties import PropertiesMenu
from widgettree import WidgetTree

Builder.load_string('''#:kivy 1.0.9
<Designer>:
    canvas_area:canvas_area
    win:win
    widget_tree_box:widget_tree_box
    leftbox:leftbox
    rightbox:rightbox
    BoxLayout:
        id:win
        orientation:'horizontal'
        #Leftbox
        BoxLayout:
            orientation:'horizontal'
            size_hint:.7,1
            #WidgetTree
            BoxLayout:
                orientation:'vertical'
                id:widget_tree_box
                size_hint_x:0.3
                Widget:
                    #This is a dummy widget to allow space for the menubar
                    size_hint_y:0.05
            #Canvas_Area and StatusBar
            BoxLayout:
                id:leftbox
                orientation:'vertical'
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
        #Right box
        BoxLayout:
            id:rightbox
            size_hint:.3,1
    Label:
        color:0,0,0,1
        text:'Canvas Area'
        text_size:(300,300)
        pos: 50, 100
            ''')

class Designer(FloatLayout):
    widget = ObjectProperty(None, allownone=True)
    
    #All components of the designer
    status_bar = ObjectProperty(None)
    canvas_area = ObjectProperty(None)
    leftbox = ObjectProperty(None)
    rightbox = ObjectProperty(None)
    win = ObjectProperty(None)
    menubar = ObjectProperty(None)
    widget_tree = ObjectProperty(None)
    widgetbar = None
    
    numeric_keys = ObjectProperty(None)
    boolean_keys = ObjectProperty(None)
    string_keys = ObjectProperty(None)
    remaining_keys = ObjectProperty(None)
    numeric_keys, boolean_keys, string_keys,\
         remaining_keys = ([] for i in range(4))
    
    def __init__(self, **kwargs):
        super(Designer, self).__init__(**kwargs)
        self.root_name = ""
        self.popup = None
        self.file = ""
        
        # A count variable to give ids to generated widget
        self.count = 0

        #This variable updates to True when ctrl is pressed
        self.ctrl_pressed = False
        
        #Instantiate the WidgetTree
        self.widget_tree = WidgetTree(self)
        self.widget_tree_box.add_widget(self.widget_tree)
        
        #Instantiate MenuBar
        self.menubar = MenuBar(designer = self, pos_hint = {'x':0,'top':1}, \
                            canvas_area = self.canvas_area, size_hint = (.70,None),height = 25)
        self.add_widget(self.menubar)
        
        #Instantiate right widgets bar
        # We update the same widgets bar, and dont create new instances everytime
        self.widgetbar = NewWidgetsMenu(self)
        self.rightbox.add_widget(self.widgetbar)
        
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
        
        #Show properties binding
        # self.widget -> updated on_touch_down in 'canvas_area'
        # So, whenever we have a new self.widget, we call show_properties
        self.bind(widget = self.show_properties)
        self.bind(widget = self.widget_tree.select_highlighted)
        
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
    
    def redraw_canvas(self, widget, *kwargs):
        ''' This function redraws the canvas of 'Layout' widgets whenever they are
        moved or resized so that it is easy to recognize them in the canvas_area.
        As the 'Layout' widgets themselves dont have a representation.'''
        widget.canvas.clear()
        thickness = 5
        with widget.canvas:
             Color(0.5, 0.5, 0.5, .5)
             Rectangle(pos = widget.pos, size = (thickness, widget.height))
             Rectangle(pos = widget.pos, size = (widget.width, thickness))
             Rectangle(pos = (widget.x,widget.top), size = (widget.width, thickness))
             Rectangle(pos = (widget.x + widget.width, widget.y), size = (thickness, widget.height))
                  
    def drag(self, widget, touch):
        ''' This function moves the widget in the canvas_area when it is 
        dragged (on_touch_move of the widget is called)'''
        if self.widget == widget:
            '''The above check is done so that only the selected widget
            which is stored in "self.widget" is moved on drag.'''
            widget.center = touch.pos

    def on_touch_down(self,touch):
        #First priority should be given to menubar as it has 
        #to be on top  of canvas_area
        if self.menubar.collide_point(*touch.pos) or self.menubar.menu_down:
            super(Designer, self).on_touch_down(touch)
        # Next we check if touch is outside the 'canvas_area' region
        elif not self.canvas_area.collide_point(*touch.pos):
            super(Designer, self).on_touch_down(touch)
        #What's remaining is the canvas_area region
        else:
            canvas_area = self.canvas_area
            temp_widget = self.pick(canvas_area, *touch.pos)
            if temp_widget is not canvas_area:
                self.widget = temp_widget
            else:
                self.widget = None
            super(Designer, self).on_touch_down(touch)
        return True
        
    def pick(self, widget, x, y):
        ret = None
        if widget.collide_point(x, y):
            ret = widget
            x2, y2 = widget.to_local(x, y)
            for child in widget.children:
                ret = self.pick(child, x2, y2) or ret
        return ret
    
    def show_properties(self, widget, value):
        '''This function is called whenever an added widget is selected
        in the canvas area. It draws the widget properties bar
        on the right, and sets up a highlighting area around the
        selected widget'''
        if value is not None:
            #We have to stop previous highlighing
            Clock.unschedule(self.highlight_at)
            #Setting up highlighting of the selected widget
            Clock.schedule_interval(self.highlight_at, 0)
            
            # Here I instantiate a new PropertiesMenu everytime.
            # Is this very expensive?
            self.rightbox.clear_widgets()
            properties_menu = PropertiesMenu(self)
            self.rightbox.add_widget(properties_menu)
        else:
            #We have to stop highlighing
            Clock.unschedule(self.highlight_at)
            self.grect.size = (0, 0)
            # Go to basic menu
            self.rightbox.clear_widgets()
            self.rightbox.add_widget(self.widgetbar)
    
    def rebuild_menu(self, node, value, parent = None):
        '''This function is called when a widget needs to be added 
        as a child to one of the added layouts in the canvas area'''
        if value:
            self.rightbox.clear_widgets()
            self.widgetbar.build_menu(parent = parent)
            self.rightbox.add_widget(self.widgetbar)
        
    def delete_item(self, instance, *largs):
        if instance.is_selected:
            parent = self.widget.parent
            parent.remove_widget(self.widget)
            self.clear_selection(True)
            #We also need to refresh the widget tree
            self.widget_tree.refresh()
            
    def clear_selection(self,*kwargs):
        '''This function takes away the highlight 
        and also nullifies the self.widget'''
        self.widget = None
        #We have to stop highlighing
        Clock.unschedule(self.highlight_at)
        self.grect.size = (0, 0)

    def highlight_at(self, *largs):
        '''A function to highlight the current self.widget'''
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
    
    def give_id(self):
        self.count = self.count + 1
        return "widget"+str(self.count) 
    
    def import_widget(self, *kwargs):
        #For testing. Point this to your generated kv file
        file_path = "~/github/kivy-designer/kv_test.py"
        #Change separator for non-unix systems
        file_name = file_path.split("/")[-1]
        file_headpath = file_path.split(file_name)[0]
        sys.path.append(file_headpath)
        imported_file = __import__(file_name[0:-3])
        for name, value in inspect.getmembers(imported_file):
            if inspect.isclass(value):
                module_name =  value.__module__
                if module_name == file_name[0:-3]:
                    temp_widget = value()
                    self.canvas_area.add_widget(temp_widget)
    
class DesignerApp(App):

    tool = ObjectProperty(None)

    def build(self):
        self.tool = Designer()
        return self.tool

if __name__ in ('__android__', '__main__'):
    DesignerApp().run()