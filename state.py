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
        self.find_ids(root)
        #print self.child_dict
        
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
    
    def find_diff(self,widget):
        '''A utility function to find differences in properties
        between a user-modified widget and a fresh instance of the same class.
        Currently its implemented by Factory building a fresh instance and 
        comparing  but later we should add a function in kivy.properties like getdefaultvalue()
        '''
        #This dict will hold the comparable properties (We skip Alias, ReferenceList and _)
        comp_dict = {}
        #This dict will ultimately hold the properties which have changed from their defaults
        diff_dict = {}
        module_name = widget.__class__.__module__
        class_name = widget.__class__.__name__
        # TODO : Check if this class is already register. If so, don't register again.
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
        if len(diff_dict) != 0:
            print "Diff in "+ class_name
        return diff_dict
        
            
        
            
            
        
            
    