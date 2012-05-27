import kivy
kivy.require('1.0.9')

from kivy.app import App
from kivy.uix.widget import Widget
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
import pkgutil
import random

Builder.load_string('''#:kivy 1.0.9
<designer>:
    canvas_area:canvas_area
    treeview:treeview
    #prog_bar:prog_bar
    #widget_box:widget_box
    BoxLayout:
        id:win
        orientation:'horizontal'
        #Canvas box
        FloatLayout:
            id:canvas_area
            size_hint:.8,1
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
                
        #widgets box
        BoxLayout:
            size_hint:.4,1
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
    canvas_area = ObjectProperty(None)
    treeview = ObjectProperty(None)
    win = ObjectProperty(None)
    saved_nodes = ObjectProperty(None)
    saved_nodes = []
    
    for entry in pkgutil.iter_modules(path=kivy.uix.__path__):
        module_name = "kivy.uix."+entry[1]
        class_name = entry[1].title()
        Factory.register(class_name, module=module_name)
        
    def build(self):
        keys=[]
        for i in pkgutil.iter_modules(path=kivy.uix.__path__):
            keys.append(i[1]) 
        keys.sort()
        node = None
        for key in keys:
            text = '%s' % key
            text = text.title()
            node = TreeViewLabel(text=text)
            node.bind(is_selected = self.add_new_widget)
            self.treeview.add_node(node)
            self.saved_nodes.append(node)
        
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