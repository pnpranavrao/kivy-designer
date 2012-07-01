#This is actually a file completely generated by the Kivy Designer (Except for this comment).
#It is fairly simple with no dynamic values or callbacks yet. I shall be using this file as input for 
#tests to generate back the UI in the Kivy-designer

### -- Start of imports --- ###
from kivy.lang import Builder
from kivy.properties import DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
### -- End of imports --- ###
### -- Start generated kv rules

Builder.load_string('''
#:import QueryDict kivy.utils.QueryDict
<MyCustomWidget>:
    height:456.0
    size_hint_x:0.8
    size_hint_y:0.8
    width:448.0
    x:49.0
    y:97.0
    ids:QueryDict({'widget1':widget1})
    Button:
        height:91.2
        id:widget1
        size_hint_x:0.2
        size_hint_y:0.2
        width:448.0
        x:49.0
        y:97.0
''')


##- Start generated class body -##
class MyCustomWidget(BoxLayout):
    ids = DictProperty({})
    def __init__(self, **kwargs):
        super(MyCustomWidget, self).__init__(**kwargs)

