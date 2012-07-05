import kivy
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeViewNode
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from treeviewproperties import TreeViewPropertyBoolean, \
 TreeViewPropertyText,TreeViewPropertyLabel
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from functools import partial

Builder.load_string('''#:kivy 1.0.9
<WidgetTree>:
    treeview:treeview
    TreeView:
        id: treeview
        size_hint_y: None
        hide_root: False
        height: self.minimum_height
''')

class WidgetTree(ScrollView):
    ''' A ScrollView class the plugs into the widget_tree_box BoxLayout on the Designer.
    These many abstractions (plus the added dummy widget) is messy, need to snip this.
    This class is responsible to keep the Widget tree updated at all times and enable selection
    and two way highlight between the widgets in the canvas_area and their TreeViewLabel representations
    in this class'''
    
    treeview = ObjectProperty(None)
    
    def __init__(self, designer, **kwargs):
        super(WidgetTree, self).__init__(**kwargs)
        self.designer = designer
        self.root = None
        
    def refresh(self, *largs):
        '''This will be called whenever a new widget is added or a widget
        is deleted.
        I might have to write a separate function to just highlight the
        selected widget in the tree'''
        #Clear old tree first
        self.clear_tree(self.treeview)
        #It all makes sense only if a root widget exists
        if self.designer.canvas_area.children:
            self.root = self.designer.canvas_area.children[0]
            self.treeview.get_root().text = self.designer.root_name
            self.draw_tree(self.root, self.treeview.get_root())
            
    def draw_tree(self, root, root_node):
        '''A recursive function to traverse the complete widget tree and
        build the WidgetTree.
        Here 'root' will be the widget in question, and 'root_node'
        a TreeViewLabel denoting the widget'''
        treeview = self.treeview
        for child in root.children:
            node = TreeViewLabel(text = child.__class__.__name__)
            treeview.add_node(node, root_node)
            self.draw_tree(child, node)
    
    def clear_tree(self,treeview):
        #Copy all current nodes in a temp list
        temp = list(treeview.iterate_all_nodes())
        #Delete them.
        for node in temp:
            treeview.remove_node(node)
            
        
        
