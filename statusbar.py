import kivy
kivy.require('1.0.9')

from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.clock import Clock
from functools import partial

Builder.load_string('''#:kivy 1.0.9
<StatusBar>
    markup:True
    text:self.text if self.text else ""
''')

class StatusBar(Label):
    
    def __init__(self,**kwargs):
        super(StatusBar, self).__init__()
        self.size_hint = kwargs.get('size_hint')
        
    def print_status(self, msg, t=3):
        """Provide a string as an argument to print it out
        in the status bar for 2 seconds"""
        self.text = "[b]Status Bar : [/b] " + msg
        Clock.unschedule(self.clear_status)
        Clock.schedule_once(self.clear_status, t)
    
    def clear_status(self, *largs):
        """Small function to clear the status bar after time seconds"""
        self.text = ""