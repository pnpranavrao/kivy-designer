import kivy
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty


class Saver():
    
    def __init__(self,root):
        # Holds the root node of the widget tree.
        self.root = root
        # Dictionary containing ids of every child widget in the tree
        self.child_dict = {}
        # Dictionary containing all imports to be made in the generated program 
        self.imports = {}
        self.find_imports()
        self.print_imports()
        self.find_ids(root)
        print "### -- Start generated kv rules"
        print "Builder.load_string(\""
        self.generate_kv(root)
        print "\""
        
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
   