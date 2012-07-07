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
        self.widget_dict = {}
        #This dict will contain elements like 
        # {node_id : child represented by the node}
        
    def refresh(self, *largs):
        '''This will be called whenever a new widget is added or a widget
        is deleted. It takes the root, and rebuilds the tree.'''
        #Clear old tree first
        self.clear_tree(self.treeview)
        #It all makes sense only if a root widget exists
        if self.designer.canvas_area.children:
            self.root = self.designer.canvas_area.children[0]
            self.treeview.get_root().text = self.designer.root_name
            self.treeview.get_root().bind(is_selected = partial(self.notify_canvas, self.root))
            self.widget_dict[self.treeview.get_root().uid] = self.root
            self.draw_tree(self.root, self.treeview.get_root())
        else:
            self.clear_tree(self.treeview)
            
    def draw_tree(self, root, root_node):
        '''A recursive function to traverse the complete widget tree and
        build the WidgetTree.
        Here 'root' will be the widget in question, and 'root_node'
        a TreeViewLabel denoting the widget'''
        treeview = self.treeview
        for child in root.children:
            node = TreeViewLabel(text = child.__class__.__name__)
            node.bind(is_selected = partial(self.notify_canvas, child))
            self.widget_dict[node.uid] = child 
            treeview.add_node(node, root_node)
            self.draw_tree(child, node)
    
    def notify_canvas(self, widget, instance, value):
        '''A function to notify the canvas_area that 'widget' has been selected
        in the WidgetTree and highlighting and property display must be 
        changed accordingly'''
        if value:
            if self.designer.widget is not widget:
                self.designer.widget = widget
                
    def select_highlighted(self, designer, widget):
        '''This function is called from the Designer class whenever
        a new widget is highlighted (when self.widget changes). So the 
        'widget' argument we have here is to to highlighted in our WidgetTree.'''
        '''The only problem with this setup is :
        Select widget in Tree > Designer.widget changed > self.select_highlighted called >
        All treeview selections cleared > Designer.widget node in tree highlighted > Stop.
        So self.select_highlighted is called unnecessarily here. You might want to maintain a
        similar selected variable to skip this problem'''
        treeview = self.treeview
        for node in treeview.iterate_all_nodes():
            node.is_selected = False
            if self.widget_dict[node.uid] is widget:
                node.is_selected = True
        
    def clear_tree(self,treeview):
        #Copy all current nodes in a temp list
        temp = list(treeview.iterate_all_nodes())
        #Delete them.
        for node in temp:
            treeview.remove_node(node)
    
    
        
            
        
        
