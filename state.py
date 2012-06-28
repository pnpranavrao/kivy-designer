import kivy
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from functools import partial
import sys
from os.path import isdir

Builder.load_string('''#:kivy 1.0.9
<SavePopup>:
    orientation:'vertical'
    filechooser:filechooser
    FileChooserListView:
        id:filechooser
        dirselect:True
    BoxLayout:
        size_hint_y:0.2
        Button:
            text:"Create new file here"
            on_release:root.create_file()
        Button:
            text:"Save"
            on_release:root.save(filechooser)
<Inputfile>:
    textbox:textbox
    orientation:'vertical'
    TextInput:
        id:textbox
    Button:
        size_hint_y:.2
        text:"Create this file and save"
        on_press:root.create_file(root.textbox)
            ''')
class Inputfile(BoxLayout):
    ''' A class for Designer.popup's 'content' field.
    This is used to accept a  new file name'''
    textbox = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(Inputfile, self).__init__(**kwargs)
        self.popup = kwargs.get('popup')
        self.designer = kwargs.get('designer')
        self.dir_path = kwargs.get('dir_path')

    def create_file(self, textbox, *largs):
        ''' A function bounded to the save button. Grabs the text in the text box 
        stores it in self.designer.file'''
        file_name = textbox.text
        # Fix-this : need to add platform specific separator here!
        self.designer.file = self.dir_path +"/"+ file_name
        self.popup.dismiss()

class SavePopup(BoxLayout):
    ''' A class for Designer.popup's 'content' field.
    This is used to display the filechooser interface'''
    filechooser = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(SavePopup, self).__init__(**kwargs)
        self.popup = kwargs.get('popup')
        self.designer = kwargs.get('designer')
        
    def save(self, filechooser, **kwargs):
        selected = filechooser.selection
        if selected:
            file = selected[0]
            if isdir(file):
                #Ignore. A file needs to be selected, not a folder.
                self.designer.status_bar.print_status\
                ("You need to select a file, not a folder for this option to work")
            else:
                self.designer.file = file
                self.popup.dismiss()
        else:
            self.designer.status_bar.print_status("Select a file, and then click save")
        
    def create_file(self, *largs):
        ''' A function bounded to the "Create new file" button in SavePopup.
        It clears  'content' and puts in the 'Inputfile' class as the new 'content'.
        So we can now accept the new filename given by the user'''
        selected = self.filechooser.selection
        if selected:
            #We need to check if this is a directory or a file.
            dir_path = selected[0]
            if isdir(dir_path):
                #prompt for filename
                input_box = Inputfile(popup = self.popup, designer = self.designer, dir_path = dir_path)
                self.popup.title = "Enter the new file name in {0}".format(dir_path.encode('ascii'))
                self.popup.content = input_box
            else : 
                self.designer.status_bar.print_status(" You need to select a folder, not a file")
            #Fix-this : Improve this. Something more intuitive
        else:
            self.designer.status_bar.print_status("Please make a selection and then click")
            
class Saver():
    
    def __init__(self, designer, root, *kwargs):
        self.designer = designer
        #Popup to specify where the generated .py file should be saved
        content = SavePopup(popup = self.designer.popup, designer = self.designer)
        self.designer.popup = Popup(title='Select location to save generated file',
                          content=content,
                          size_hint=(None, None), size=(400, 400))
        self.designer.popup.open()
        self.designer.popup.bind(on_dismiss = partial(self.write_file, "SavePopup"))
        # Holds the root node of the widget tree.
        self.root = root
        # Dictionary containing ids of every child widget in the tree
        self.child_dict = {}
        # Dictionary containing all imports to be made in the generated program 
        self.imports = {}
        self.find_imports()
        self.find_ids(root)
        
    def write_file(self, popup_type, *largs):
        '''A function to write the file to disk using file information
        from self.designer.file'''
        if popup_type == "SavePopup":
            if self.designer.file != "":
                self.designer.file = self.designer.file.encode('ascii')
                try:
                    sys.stdout = open(self.designer.file, 'w')
                    self.print_imports()
                    print "### -- Start generated kv rules"
                    print "Builder.load_string(\""
                    self.generate_kv(self.root)
                    print "\""
                    self.designer.status_bar.print_status\
                    ("All okay. File saved at {0}".format(self.designer.file.encode('ascii')))
                    sys.stdout = sys.__stdout__
                except Exception as err:
                    self.designer.file = ""
                    print err
            
    def find_ids(self,root):
        ''' A utility funtion to recursively travel from the root node
        and extract the id of every widget in the whole tree'''
        for child in root.children:
            self.child_dict[child]=child.id
            #print self.find_diff(child)
            if len(child.children) is not 0:
                self.find_ids(child)
    
    def find_imports(self):
        ''' A utility funtion to find all the imports required
        in the file that will be generated '''
        widgets = self.child_dict.keys()
        for widget in widgets:
            module_name = widget.__class__.__module__
            class_name = widget.__class__.__name__
            self.imports[class_name] = module_name
            
    def print_imports(self):
        print "### -- Start of imports --- ###"
        print "from kivy.lang import Builder"
        for key, value in self.imports.iteritems():
            print "from {0} import {1}".format(value, key)
        print "### -- End of imports --- ###"
    
    def find_diff(self,widget):
        '''A utility function to find differences in properties
        between a user-modified widget and a fresh instance of the same class.
        Currently its implemented by Factory building a fresh instance and 
        comparing  but later we should add a function in kivy.properties like getdefaultvalue()
        This returns a dictionary of {property:values}
        '''
        #This dict will hold the comparable properties (We skip Alias, ReferenceList and _)
        comp_dict = {}
        #This dict will ultimately hold the properties which have changed from their defaults
        diff_dict = {}
        module_name = widget.__class__.__module__
        class_name = widget.__class__.__name__
        # TODO : Check if this class is already registered. If so, don't register again.
        Factory.register(class_name, module=module_name)
        factory_caller = getattr(Factory, class_name)
        new_widget = factory_caller()
        #Skipping certain types of properties
        for prop, value in new_widget.properties().iteritems():
            if prop.startswith('_'):
                continue
            if isinstance(value, AliasProperty):
                continue
            if isinstance(value, ReferenceListProperty):
                continue
            comp_dict[prop] = getattr(new_widget, prop)
        #Now compare these properties with the user created one
        for prop,value in comp_dict.iteritems():
            if value != getattr(widget, prop):
                diff_dict[prop] = getattr(widget, prop)
#        if len(diff_dict) != 0:
#            print "Diff in "+ class_name
        return diff_dict
        
    def generate_kv(self, root, tab_string = ""):
        '''This function takes a root widget, and recursively prints
        a .kv file using properties found using the find_diff function.
        tab_string should specify at what position this 
        root's properties should should start printing.'''
        class_name = root.__class__.__name__
        if tab_string == "":
            print "<{0}>:".format(class_name)
        else:
            print "{0}{1}:".format(tab_string,class_name)
        # Increment tab_string by 4 spaces
        tab_string += "    "
        # Construct diff_dict of present root widget
        diff_dict = self.find_diff(root)
        self.print_diffdict(diff_dict, tab_string)
        children = root.children
        # Recursively repeat the above process for 
        # .. the current root widget
        for child in children:
            self.generate_kv(child, tab_string = tab_string)
        
    def print_diffdict(self, diff_dict, tab_string ):
        ''' This function prints properties according to a 
        tab_string level when passed a diff_dict'''
        '''Fix-This : Here we cannot check for Numeric, Boolean, and
        other properties. All this must be done while constructing the diffdict
        Will this lead to problems later on? '''
        items = diff_dict.items()
        items.sort()
        for prop, value in items:
            if isinstance(value, bool):
                print "{0}{1}:{2}".format(tab_string, prop, str(value))
                continue
            if isinstance(value, float):
                print "{0}{1}:{2}".format(tab_string, prop, value)
                continue
            if isinstance(value, str):
                if prop == "id":
                    print "{0}{1}:{2}".format(tab_string, prop, value)
                else:
                    value = "\"" + value + "\""
                    print "{0}{1}:{2}".format(tab_string, prop, value)
            else:
                pass
                #print "NO" + prop + repr(value) 
                #FIX-This : Not yet printing other types of properties, 
                # as editing of those types aren't implemented yet.
   