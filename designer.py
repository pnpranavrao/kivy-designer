import kivy
kivy.require('1.0.9')

from kivy.app import App
from kivy.uix.widget import Widget
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
        Translate, Rotate,Scale
from kivy.uix.treeview import TreeViewNode
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from kivy.factory import Factory
from kivy.vector import Vector
from kivy.clock import Clock
import random
from functools import partial

Builder.load_string('''#:kivy 1.0.9
<designer>:
    status_bar:status_bar
    canvas_area:canvas_area
    treeview:treeview
    win:win
    #widget_box:widget_box
    BoxLayout:
        id:win
        orientation:'horizontal'
        BoxLayout:
            size_hint:.7,1
            orientation:'vertical'
            #Canvas box
            FloatLayout:
                size_hint:1,.95
                id:canvas_area
                canvas:
                    Color:
                        rgb:1,.9,.8
                    Rectangle:
                        pos: self.x, self.y
                        size: self.width,self.top
                Label:
                    color:0,0,0,1
                    text:'Canvas Area'
                    text_size:(300,300)
                    pos:150,200
                    #Doubts :
                    #size_hint:0.2,0.2 >>Also screws things up
                    #pos_hint:(.5,.5) >> Why doesn't this work?
                    #pos:root.width/2,root.top/2 >> how to reference FloatLayout?
            #Statusbar
            Label:
                markup:True
                id:status_bar
                text:self.text if self.text else ""
                size_hint:1,.05
                    
        #widgets box
        BoxLayout:
            size_hint:.3,1
            ScrollView:
                TreeView:
                    id: treeview
                    size_hint_y: None
                    hide_root: True
                    height: self.minimum_height
                    
<TreeViewProperty>:
    height:25
    Label:
        bold:True
        text:root.lkey if root.lkey else ""
        text_size: (self.width,None)
        width:self.width
        size_hint_x: None
    Label:
        shorten:True
        color:0.39,1,.2,1
        text:root.rkey if root.rkey else ""
        text_size: (self.width,None)
        width:self.width
        size_hint_x: None
                    ''')

class TreeViewProperty(BoxLayout,TreeViewNode):
    lkey = ObjectProperty(None)
    rkey = ObjectProperty(None)
    
class designer(FloatLayout):
    status_bar = ObjectProperty(None)
    canvas_area = ObjectProperty(None)
    treeview = ObjectProperty(None)
    win = ObjectProperty(None)
    saved_nodes = ObjectProperty(None)
    saved_nodes = []
    widget_list = {}
    # get any widgets in kivy.uix directory
    for cls in Factory.classes:
        module_string = str(Factory.classes[cls]['module'])
        # if module is from current projects uix directory(user defined widgets) or 'kivy.uix' (kivy defined widgets)
        if module_string.startswith(('uix', 'kivy.uix')):
            widget_list[cls]=str(Factory.classes[cls]['module'])
            Factory.register(cls,module=widget_list[cls])
        
    def build(self):
        keys=[]
        for cls in self.widget_list:
            if cls == "Camera":
                '''This is because there seems to be some bug in Gstreamer 
                when we load a camera widget and don't use it '''
                continue
            try:
                factory_caller = getattr(Factory,str(cls))
                new_widget = factory_caller()
                if isinstance(new_widget,Layout):
                    continue
                if isinstance(new_widget,Widget):
                    keys.append(cls)
            except Exception as err:
                self.print_status(err.message)
        keys.append('Camera')
        keys.sort()
        node = None
        for key in keys:
            text = '%s' % key
            node = TreeViewLabel(text=text)
            node.bind(is_selected = self.add_new_widget)
            self.treeview.add_node(node)
            self.saved_nodes.append(node)
    
    def print_status(self,msg):
        """Provide a string as an argument to print it out in the status bar for 2 seconds"""
        label = self.status_bar
        label.text = "[b]Status Bar[/b] "+msg
        g = lambda x,y:""
        Clock.schedule_interval(self.clear_status, 2)
        
    def clear_status(self,*largs):
        """Small function to clear the status bar after n seconds"""
        self.status_bar.text = ""
        
    def add_new_widget(self, instance, value,index=-1, *l):
        if instance.is_selected:
            class_name = instance.text
            factory_caller = getattr(Factory,class_name)
            new_widget = factory_caller(size_hint=(.2,.2))
            new_widget.bind(on_touch_move = self.drag)
            new_widget.bind(on_touch_up = self.show_properties)
            self.canvas_area.add_widget(new_widget)
            instance.is_selected = False

    def drag(self,widget,touch):
        if widget.collide_point(touch.x,touch.y):
            widget.center = touch.pos
            
    def show_properties(self,widget,touch):
        treeview = self.treeview
        temp = list(treeview.iterate_all_nodes())
        for node in temp:
            treeview.remove_node(node)
        #Why does treeview loose all sense of parents?
        #Why aren't nodes added to it? Do we have to return this treeview?
        treeview.height = 30
        node = TreeViewLabel(text="< BACK TO ADD MORE WIDGETS",color=[1,1,0,1],bold=True)
        node.bind(is_selected=self.build_menu)
        treeview.add_node(node)
        treeview.height = 25
        keys = widget.properties().keys()
        keys.sort()
        node = None
        for key in keys:
            text = '%s' % key
            node = TreeViewProperty()
            node.lkey = text
            node.rkey = str(getattr(widget,key))
            node.bind(is_selected = self.print_info)
            treeview.add_node(node)
                    
    def print_info(self,instance,*largs):
        if instance.is_selected:
            print instance.lkey,instance.rkey
            instance.is_selected = False
            
    def build_menu(self,instance,*largs):
        if instance.is_selected:
            treeview = self.treeview
            temp = list(treeview.iterate_all_nodes())
            for node in temp:
                treeview.remove_node(node)
            for node in self.saved_nodes:
                treeview.add_node(node)
            instance.is_selected = False    
        
class DesignerApp(App):
    tool = ObjectProperty(None)
    def build(self):
        self.tool = designer()
        self.tool.build()
        return self.tool
    
#Factory.register("TreeViewProperty",TreeViewProperty)

if __name__ in ('__android__', '__main__'):
    DesignerApp().run()    