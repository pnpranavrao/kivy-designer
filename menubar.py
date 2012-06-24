import kivy
kivy.require('1.0.9')

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.clock import Clock
import random
import weakref
from functools import partial
from state import Saver

Builder.load_string('''#:kivy 1.0.9
<MenuBar>:
    size:self.size
    
<MenuTreeView>:
    size_hint_y: None
    hide_root: True
    height: self.minimum_height
    
<Toggle1>:
    border:(1, 1, 1, 1)
    
''')

class MenuTreeView(TreeView):
    
    def __init__(self, **kwargs):
        super(MenuTreeView, self).__init__(**kwargs)
        self.bind(selected_node = self.on_node_selected)
        # Fix-this : Above not working.
        
    def on_node_selected(self, treeview, *kwargs):
        ''' Function to close the menu as soon as a selection is done'''    
        if treeview.selected_node:
            #Deselect node first
            #treeview._selected_node = None
            # Fix-this :  There appears to toggle a selected node. Investigate
            single_menu = self.parent.parent.parent
            # Need to find a better way to get the parent - single_menu.
            # The problem with the above method is that you can't use this class
            # for nested menus i.e MenuTreeView inside MenuTreeView
            menus = single_menu.children
            for menu in menus:
                for child in menu.children:
                    if isinstance(child, ToggleButton):
                        child.state = 'normal'


class Toggle1(ToggleButton):
    pass

class TreeViewLabel1(Label, TreeViewNode):
    '''Custom TreeViewLabel style 1 : Used for menu items'''
    def __init__(self,**kwargs):
        super(TreeViewLabel1,self).__init__(**kwargs)
        self.height = 20
        self.odd_color = (0, 0, 0, 0.7)
        self.even_color = (0, 0, 0, 1)
        self.bold = True
        self.color_selected = (0.5, .7, 1, 1)

class MenuBar(BoxLayout):
    '''The structure of the menubar is as follows:
    MenuBar(BoxLayout-horizontal)
        *SingleMenuItem(BoxLayout-vertical)
            *ToggleButton
            *ScrollView
                *MenuTreeView
    '''
    def on_touch_down(self, touch):
        '''This is necessary to close the menus if the mouse is 
        clicked anywhere else other than the menu when its open'''
        if self.menu_down:
            if not self.collide_point(*touch.pos):
                menus = self.children
                for menu in menus:
                    for child in menu.children:
                        if isinstance(child, ToggleButton):
                            child.state = 'normal'
            else:
                super(MenuBar, self).on_touch_down(touch)
            return True
        elif self.collide_point(*touch.pos):
          super(MenuBar, self).on_touch_down(touch)
          return True
        
    def __init__(self,**kwargs):
        super(MenuBar,self).__init__(**kwargs)
        self.canvas_area = kwargs.get('canvas_area')
        self.menu_down = False
        #File Menu
        treeview_file = MenuTreeView()
        items    = ["Open...", "Save", "Save As..", "Sync git repo", "Quit.."]
        for item in items:
            node = TreeViewLabel1(text=item)
            if item in ["Save","Save As.."]:
                node.bind(is_selected = self.save_state)
            treeview_file.add_node(node)
        #Edit menu
        treeview_edit = MenuTreeView()
        items = ["Undo", "Redo", "Cut", "Copy", "Paste"]
        for item in items:
            node = TreeViewLabel1(text=item)
            treeview_edit.add_node(node)
        #Program menu
        treeview_program = MenuTreeView()
        items = ["Run", "Pause", "Stop", "Stop All"]
        for item in items:
            node = TreeViewLabel1(text=item)
            treeview_program.add_node(node)
        self.add_menu_item("File", treeview_file)
        self.add_menu_item("Edit", treeview_edit)
        self.add_menu_item("Program", treeview_program)
        return 
    
    def save_state(self, node_selected, value):
        if value == True:
            a = Saver(self.canvas_area)
            
    
    def add_menu_item(self,item_name,treeview_object):
        #Create a button with the name 'item_name'
        item_button = Toggle1(text = item_name, pos = (0,self.top), \
                    group = "menu"+str(self), height = self.height, size_hint_y = None)
        # Create a ScrollView and add its treeview. This will
        # be our scrollable menu
        parent_scrollview = ScrollView()
        parent_scrollview.add_widget(treeview_object)
        single_menu_item = BoxLayout(orientation='vertical',size_hint_y = 1)
        #This 'single_menu_item' will be the container for a single menu.
        # It would consist of a toggle button and a scrollview
        item_button.bind(state=partial(self.__add_scrollview, item_button, \
                                       single_menu_item, parent_scrollview))
        #On click should give a function that adds our scrollview to the single_menu_list
        single_menu_item.add_widget(item_button)
        self.add_widget(single_menu_item)

    def __add_scrollview(self,*kwargs):
        '''Function to attach scrollview of a single menu'''
        item_button, menu_list, parent_scrollview, \
                    instance, state = kwargs
        children_list = list(menu_list.children)
        last_child = children_list[len(children_list)-1]
        if state=='down':
            menu_list.add_widget(parent_scrollview)
            self.space_siblings(menu_list.parent, menu_list, True)
            menu_list.parent.height = min(last_child.height +\
            parent_scrollview.children[0].height, menu_list.parent.parent.height)
            self.menu_down = True
        else:
            children_list = list(menu_list.children)
            last_child = children_list[len(children_list)-1]
            menu_list.clear_widgets()
            self.space_siblings(menu_list.parent, menu_list, False)
            menu_list.add_widget(last_child)
            menu_list.parent.height = last_child.height
            self.menu_down = False

    def space_siblings(self, obj, skip, add):
        for child in obj.children:
            #We shouldn't add the dummy widget to the opened menu
            if child is not skip:
                if add:
                    try:
                        child.add_widget(child.spacing_widg)
                    except AttributeError:
                        child.spacing_widg = Widget()
                        child.add_widget(child.spacing_widg)
                else:
                   child.remove_widget(child.spacing_widg)