import kivy
kivy.require('1.0.9')

from kivy.app import App
from kivy.uix.widget import Widget
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
from kivy.factory import Factory
from kivy.vector import Vector
from kivy.clock import Clock
import random
import weakref
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
                        rgb:.9,.9,.8,
                    Rectangle:
                        pos: self.x, self.y
                        size: self.width,self.top
                Label:
                    color:0,0,0,1
                    text:'Canvas Area'
                    text_size:(300,300)
                    pos:150,200
            #Statusbar
            Label:
                size_hint:1,.05
                markup:True
                id:status_bar
                text:self.text if self.text else ""
<<<<<<< Updated upstream
                
                    
=======
>>>>>>> Stashed changes
        #widgets box
        BoxLayout:
            size_hint:.3,1
            ScrollView:
                TreeView:
                    id: treeview
                    size_hint_y: None
                    hide_root: True
                    height: self.minimum_height
                    
<TreeViewPropertyLabel>:
    toggle:toggle
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
    ToggleButton:
        id:toggle
        border:0,0,0,0
        #on_state:.edit_properties()
        
<TreeViewPropertyText>:
    textbox:textbox
    height:25
    Label:
        bold:True
        text:root.key if root.widget else ""
        text_size: (self.width,None)
        width:self.width
        size_hint_x: None
    TextInput:
        id:textbox
        shorten:True
        color:0.39,1,.2,1
        text:repr(getattr(root.widget,root.key)) if root.widget else ''
        text_size: (self.width,None)
        width:self.width
        size_hint_x: None

<TreeViewPropertyBoolean>:
    toggle:toggle
    height:25
    Label:
        bold:True
        text:root.key if root.widget else ""
        text_size: (self.width,None)
        width:self.width
        size_hint_x: None
    ToggleButton:
        id:toggle
        shorten:True
        color:0.39,1,.2,1
        state:self.state
        text:"    True" if toggle.state=='down' else "   False"
        #How do we set alignment in this text?
        text_size: (self.width,None)
        width:self.width
        size_hint_x: None
            ''')


class TreeViewPropertyLabel(BoxLayout,TreeViewNode):
    '''This is a node structure that contains 2 labels 
    and a toggle. A toggle state change, triggers a 
    textinput box and accepts changes'''
    layout = ObjectProperty(None)
    widget = ObjectProperty(None)
    lkey = ObjectProperty(None)
    rkey = ObjectProperty(None)
    toggle = ObjectProperty(None)
    
"""Lesson learnt : In the .kv file, you can only bind properties to functions
 of the same class. So as TreeViewPropertyLabel/Text becomes a different class, passing
 the parameters between these two classes become very messy. Commenting the approach taken below
 as it was giving rise to segmentation faults."""
    
class TreeViewPropertyText(BoxLayout,TreeViewNode):
    lkey = ObjectProperty(None)
    rkey = ObjectProperty(None)
    layout = ObjectProperty(None)
    toggle = ObjectProperty(None)
    textbox = ObjectProperty(None)
    widget_ref = ObjectProperty(None, allownone=True)

    def _get_widget(self):
        wr = self.widget_ref
        if wr is None:
            return None
        wr = wr()
        if wr is None:
            self.widget_ref = None
            return None
        return wr
    widget = AliasProperty(_get_widget, None, bind=('widget_ref', ))
    key = ObjectProperty(None, allownone=True)

class TreeViewPropertyBoolean(BoxLayout,TreeViewNode):
    lkey = ObjectProperty(None)
    toggle = ObjectProperty(None)
    key = ObjectProperty(None, allownone=True)
    widget_ref = ObjectProperty(None, allownone=True)

    def _get_widget(self):
        wr = self.widget_ref
        if wr is None:
            return None
        wr = wr()
        if wr is None:
            self.widget_ref = None
            return None
        return wr
    widget = AliasProperty(_get_widget, None, bind=('widget_ref', ))
    
<<<<<<< Updated upstream
    widget_ref = ObjectProperty(None, allownone=True)

    def _get_widget(self):
        wr = self.widget_ref
        if wr is None:
            return None
        wr = wr()
        if wr is None:
            self.widget_ref = None
            return None
        return wr
    widget = AliasProperty(_get_widget, None, bind=('widget_ref', ))
    key = ObjectProperty(None, allownone=True)

class TreeViewPropertyBoolean(BoxLayout,TreeViewNode):
    lkey = ObjectProperty(None)
    toggle = ObjectProperty(None)
    key = ObjectProperty(None, allownone=True)
    widget_ref = ObjectProperty(None, allownone=True)

    def _get_widget(self):
        wr = self.widget_ref
        if wr is None:
            return None
        wr = wr()
        if wr is None:
            self.widget_ref = None
            return None
        return wr
    widget = AliasProperty(_get_widget, None, bind=('widget_ref', ))
    
=======
>>>>>>> Stashed changes
   
class designer(FloatLayout):
    widget = ObjectProperty(None)
    status_bar = ObjectProperty(None)
    canvas_area = ObjectProperty(None)
    treeview = ObjectProperty(None)
    win = ObjectProperty(None)
    saved_nodes = ObjectProperty(None)
    saved_nodes = []
    widget_list = {}
    exclude_list = ["VideoPlayer","VideoPlayerVolume","VideoPlayerPlayPause","VideoPlayerProgressBar"]
    #Get any widgets in kivy.uix directory
    for cls in Factory.classes:
        if cls in exclude_list:
            continue
        module_string = str(Factory.classes[cls]['module'])
        # If module is from current projects uix directory(user defined widgets)
        # or 'kivy.uix' (kivy defined widgets)
        if module_string.startswith(('uix', 'kivy.uix')):
            widget_list[cls]=str(Factory.classes[cls]['module'])
            Factory.register(cls,module=widget_list[cls])
            
    def __init__(self,**kwargs):
        super(designer, self).__init__(**kwargs)
        with self.canvas.after:
            self.gcolor = Color(1, 1, 0, .25)
            PushMatrix()
            self.gtranslate = Translate(0, 0, 0)
            self.grotate = Rotate(0, 0, 0, 1)
            self.gscale = Scale(1.)
            self.grect = Rectangle(size=(0, 0))
            PopMatrix()
        
    def build(self):
        '''Builds the widget_menu for the first time, and this function is never
        called again. While building all the widget nodes are saved in a list called
        self.saved_nodes. In future drawing of the widget menu, this list is used'''
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
    
    def print_status(self,msg,t=3):
        """Provide a string as an argument to print it out in the status bar for 2 seconds"""
        label = self.status_bar
        label.text = "[b]Status Bar : [/b] "+msg
        Clock.unschedule(self.clear_status)
        Clock.schedule_once(self.clear_status,t)
        
    def clear_status(self,*largs):
        """Small function to clear the status bar after time seconds"""
        self.status_bar.text = ""
        
    def add_new_widget(self, instance, value,index=-1, *l):
        '''This function is called whenever a new widget needs to be added
        on to the canvas_area. It creates the widget and binds it with drag and 
        show_properties functions'''
        if instance.is_selected:
            class_name = instance.text
            factory_caller = getattr(Factory,class_name)
            temp_pos_hint = (random.random(),random.random())
            '''The above is a temp solution as widgets in the same spot 
            stick due to same on_touch_move calls. Will have to offer some 
            kind of layer options support (temp_pos_hint[0],temp_pos_hint[1])'''
            new_widget = factory_caller(size_hint=(0.2,0.2),pos=self.canvas_area.pos)
            new_widget.bind(on_touch_move = self.drag)
            new_widget.bind(on_touch_down = self.show_properties)
            self.canvas_area.add_widget(new_widget)
            instance.is_selected = False

    def drag(self,widget,touch):
        if widget.collide_point(touch.x,touch.y):
            widget.center = touch.pos
            
    def show_properties(self,widget,touch):
        '''This function is called whenever an added widget is selected in the canvas area.
        It draws the widget properties bar on the right, and sets up a highlighting area around
        the selected widget'''
        
        #Cleaning up old treeview selections
        node = self.treeview.selected_node
        self.treeview.toggle_node(node)
        
        self.print_status("Focussed on %s"%(str(widget)),t=6)
        self.widget = widget
        treeview = self.treeview
        temp = list(treeview.iterate_all_nodes())
        for node in temp:
            treeview.remove_node(node)
        
        '''Adding a back button'''
        treeview.height = 30
        node = TreeViewLabel(text="< BACK TO ADD MORE WIDGETS",color=[1,1,0,1],bold=True)
        node.bind(is_selected=self.build_menu)
        treeview.add_node(node)
        
        '''Adding a delete button'''
        node = TreeViewLabel(text= "Delete this widget",color=[1,0,0,1])
        node.bind(is_selected=self.delete_item)
        treeview.add_node(node)
        treeview.height = 25
        
        wk_widget = weakref.ref(widget)
        keys = widget.properties().keys()
        keys.sort()
        node = None
        for key in keys:
            text = '%s' % key
            wk_widget = weakref.ref(widget)
            if isinstance(widget.property(key),BooleanProperty):
                node = TreeViewPropertyBoolean(key=key,widget_ref=wk_widget)
                node.toggle.bind(state=partial(self.save_properties,widget,key))
            else:
                node = TreeViewPropertyText(key=key,widget_ref=wk_widget)
                node.textbox.bind(text=partial(
                    self.save_properties,widget,key))
            treeview.add_node(node)
            Clock.schedule_interval(self.highlight_at,0)
    
    def delete_item(self,instance,*largs):
        if instance.is_selected:
            canvas_area = self.canvas_area
            canvas_area.remove_widget(self.widget)
            self.build_menu(True)
            
            #We have to stop highlighing
            Clock.unschedule(self.highlight_at)
            self.grect.size = (0,0)
            #self.treeview.toggle_node()
            
            
    def highlight_at(self,*largs):
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
                        
    def save_properties(self,widget,key,instance,value):
        prop = widget.property(key)
        self.print_status(repr(prop))
        
        dtype = None
        if isinstance(prop, AliasProperty):
            if type(value) in (unicode, str):
                dtype = 'string'
            elif type(value) in (int, float):
                dtype = 'numeric'
        
        if isinstance(prop,NumericProperty) or dtype=='numeric':
            try:
                setattr(widget,key,float(instance.text))
            except:
                self.print_status("[Numeric] This value isn't supported", 1)
        if isinstance(prop,StringProperty) or dtype=='string':
            try:
                setattr(widget,key,instance.text)
            except:
                self.print_status("[String] This value isn't supported", 1)
        if isinstance(prop,BooleanProperty):
            try:
                if instance.state=='down':
                    setattr(widget,key,True)
                if instance.state=='normal':
                    setattr(widget,key,False)
            except:
                self.print_status("[Boolean] This value couldn't be saved")
            
    def build_menu(self,instance,*largs):
        '''This is a general purpose function that builds the main menu at anytime
        when it called with a True value. It uses the list self.saved_nodes to 
        draw the main widget menu'''
        check = False
        try:
            check = instance.is_selected
        except:
             pass
        if check or instance:
            treeview = self.treeview
            temp = list(treeview.iterate_all_nodes())
            for node in temp:
                treeview.remove_node(node)
            for node in self.saved_nodes:
                treeview.add_node(node)
            
class DesignerApp(App):
    tool = ObjectProperty(None)
    def build(self):
        self.tool = designer()
        self.tool.build()
        return self.tool

if __name__ in ('__android__', '__main__'):
    DesignerApp().run()    