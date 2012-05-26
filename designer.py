import kivy
kivy.require('1.0.9')
import random
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
from kivy.uix.treeview import TreeViewNode
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from kivy.factory import Factory
import pkgutil

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
                    rgb:0,.1,.5
                Rectangle:
                    pos: self.x, self.y
                    size: self.width,self.top
            Label:
                text:'Canvas Area'
                text_size:(300,300)
                pos:150,200
                #Doubts :
                #size_hint:0.2,0.2 >>Also screws things up
                #pos_hint:(.5,.5) >> Why doesn't this work?
                #pos:root.width/2,root.top/2 >> how to reference FloatLayout?
                
        #widgets box
        BoxLayout:
            size_hint:.2,1
            ScrollView:
                TreeView:
                    id: treeview
                    size_hint_y: None
                    hide_root: True
                    height: self.minimum_height
                    TreeViewLabel:
                        pos_hint:None,.5
                        text:'Widgets'
                        text_size:self.width,None
                        width:150
                        height:200
                        size_hint_x: None
                    TreeViewLabel:
                        text:'Button'
#<TreeViewProperty>:
#    Label:
#        text_size: (self.width, None)
#        width: 150
#        size_hint_x: None
                
#        FloatLayout:
#            id:widget_box
#            size_hint:0.2,1
#            pos_hint:.8,0
#            Widget:
#                pos:self.parent.pos
#                id:prog_bar
#                on_touch_move:root.drag(*args)
#                canvas:
#                    Color:
#                        rgb:.1,.6,.7
#                    Rectangle:
#                        pos:self.pos
#                        size:self.size
#                Label:
#                    pos:self.parent.pos
#                    text:'Progress Bar'
#                        
#            Widget:
#                #pos_hint:0,.3
#                canvas:
#                    Color:
#                        rgb:.2,.8,.2
#                    Rectangle:
#                        pos:self.pos
#                        size:self.size
#                Label:
#                    pos:self.parent.pos
#                    text:'Switch'
#            Widget:
#                canvas:
#                    Color:
#                        rgb:.2,.9,.7
#                    Rectangle:
#                        pos:self.pos
#                        size:self.size
#                Label:
#                    pos:self.parent.pos
#                    text:'Button'
                       ''')

#class TreeViewProperty(BoxLayout,TreeViewNode):
#    pass
    #lkey = ObjectProperty(None)
    
class designer(FloatLayout):
    canvas_area = ObjectProperty(None)
    treeview = ObjectProperty(None)
    win = ObjectProperty(None)
    
    for entry in pkgutil.iter_modules(path=kivy.uix.__path__):
        module_name = "kivy.uix."+entry[1]
        class_name = entry[1].title()
        Factory.register(class_name, module=module_name)
        
    def drag(self,widget,touch):
        if widget.collide_point(touch.x,touch.y):
            widget.x = touch.x-widget.width/2
            widget.y = touch.y-widget.top/2
        
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
            
    def add_new_widget(self, instance, value,index=-1, *l):
        class_name = instance.text
        factory_caller = getattr(Factory,class_name)
        new_widget = factory_caller(size_hint=(.2,.2))
        self.canvas_area.add_widget(new_widget)
            
class DesignerApp(App):
    tool = ObjectProperty(None)
    def build(self):
        self.tool = designer()
        self.tool.build()
        return self.tool
    
    
        
#Factory.register("TreeViewProperty",TreeViewProperty)

if __name__ in ('__android__', '__main__'):
    DesignerApp().run()    