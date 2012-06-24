import kivy
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeViewNode
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from treeviewproperties import TreeViewPropertyBoolean, \
 TreeViewPropertyText,TreeViewPropertyLabel
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.lang import Builder
import weakref
from functools import partial


Builder.load_string('''#:kivy 1.0.9
<PropertiesMenu>:
    treeview:treeview
    TreeView:
        id: treeview
        size_hint_y: None
        hide_root: True
        height: self.minimum_height
            ''')

class PropertiesMenu(ScrollView):
    '''This class is used to return a scrollable treeview of all properties
    of 'Designer.widget'.
    It also saves any changes made to this widget by the user.'''
    treeview = ObjectProperty(None)
        
    def __init__(self, designer, **kwargs):
       super(PropertiesMenu, self).__init__(**kwargs)
       self.designer = designer
       self.status_bar = designer.status_bar
       widget = designer.widget
       designer.status_bar.print_status("Focussed on %s"%(str(widget)), t=6)
       
       self.numeric_keys, self.boolean_keys, self.string_keys,\
        self.remaining_keys = ([] for i in range(4))

       treeview = self.treeview
       '''Adding a back button'''
       treeview.height = 30
       node = TreeViewLabel(text="< BACK TO ADD MORE WIDGETS", \
                            color=[1, 1, 0, 1], bold=True)
       node.bind(is_selected = self.designer.rebuild_menu)
       node.bind(is_selected = self.designer.clear_selection)
       #Is this the right way to call 2 functions from a property change?
       treeview.add_node(node)
       
       '''If the widget is a layout, we need to provide
       an option to add more widgets to this layout'''
       if isinstance(widget,Layout):
           treeview.height = 30
           node = TreeViewLabel(text="Add widgets to this Layout", \
                                color=[.4, 1, 0, 1])   
           node.bind(is_selected= partial(designer.rebuild_menu, parent = widget))
           # Fix-this : Above's parent argument is not being passed :(
           treeview.add_node(node)
           
       '''Adding a delete button'''
       node = TreeViewLabel(text= "Delete this widget",\
                            color=[1, 0, 0, 1])
       node.bind(is_selected=self.designer.delete_item)
       treeview.add_node(node)
       
       treeview.height = 25
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
