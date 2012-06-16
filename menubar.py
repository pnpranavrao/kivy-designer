import kivy
kivy.require('1.0.9')

from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.clock import Clock
import random
import weakref
from functools import partial

Builder.load_string('''#:kivy 1.0.9
<MenuBar>:
    size:self.size
    
<MenuTreeView>:
    size_hint_y: None
    hide_root: True
    height: self.minimum_height
''')

class MenuTreeView(TreeView):
    pass

class MenuBar(BoxLayout):
    '''The structure of the menubar is as follows:
    MenuBar(BoxLayout-horizontal)
        *SingleMenuItem(BoxLayout-vertical)
            *ToggleButton
            *ScrollView
                *MenuTreeView
    '''
    def __init__(self,**kwargs):
        super(MenuBar,self).__init__(**kwargs)
        return 
        
    def add_menu_item(self,item_name,treeview_object):
        #Create a button with the name 'item_name'
        item_button = ToggleButton(size = (10,5),text = item_name)
        '''Shouldn't size/pos_hint in the above initialization decide values
            based on its parent, i.e the BoxLayout single_menu_item? 
            Why doesn't it obey it? '''   
        with item_button.canvas:
            border=(0, 0, 0, 0)
#       On click should give a function that adds a treeview to the single_menu_list
        single_menu_item = BoxLayout(orientation='vertical',size = (self.x,200),pos = (self.pos))
        '''same case in the above initialization. The hint properties dont seem to obey 
            their parent, the MenuBar BoxLayout in this case'''
        item_button.bind(state=partial(self.__add_treeview,item_button,treeview_object,single_menu_item))
        single_menu_item.add_widget(item_button)
        self.add_widget(single_menu_item)
                 
    def __add_treeview(self,item_button,treeview_object,menu_list,instance,*kwargs):
        if instance.state=='down':
            parent_scrollview = ScrollView(size=(200,200))
            parent_scrollview.add_widget(treeview_object)
            menu_list.add_widget(parent_scrollview)
        else:
            children_list = list(menu_list.children)
            menu_list.clear_widgets()
            menu_list.add_widget(children_list[1])
        
        