import kivy
kivy.require('1.0.9')

from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.uix.treeview import TreeViewNode
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from kivy.factory import Factory
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.lang import Builder
import weakref
from functools import partial

Builder.load_string('''<TreeViewPropertyLabel>:
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

class TreeViewPropertyLabel(BoxLayout, TreeViewNode):
    '''This is a node structure that contains 2 labels and a
toggle. A toggle state change, triggers a
textinput box and accepts changes'''

    layout = ObjectProperty(None)
    widget = ObjectProperty(None)
    lkey = ObjectProperty(None)
    rkey = ObjectProperty(None)
    toggle = ObjectProperty(None)

"""Lesson learnt : In the .kv file, you can only bind
properties to functions of the same class. So as
TreeViewPropertyLabel/Text becomes a different class,
passing the parameters between these two classes become
very messy. Commenting the approach taken below as it
was giving rise to segmentation faults."""


class TreeViewPropertyText(BoxLayout, TreeViewNode):
    textbox = ObjectProperty(None)
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


class TreeViewPropertyBoolean(BoxLayout, TreeViewNode):
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
