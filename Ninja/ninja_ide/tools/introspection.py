from rope.base import pycore
from rope.base import project
from rope.base.pyobjects import AbstractClass, AbstractFunction
from rope.base.pynames import DefinedName, AssignedName


def create_signature(name, params):
    return '%s(%s)' % (name, ','.join([p for p in params]))


def inspect_file(path_to_file, fileName):
    '''
    Return a tuple with the structure below
    (globals, classes, functions).
    
    *classes* is a list with the strcuture below:
        {'name': FooClass'', 'methods': [], 'attributes':[], 'superclasses': []}.
        name a string with the class name.
        methods contains a list of strings.
        attributes contains a list of strings.
        superclasses contains a list of strings.
    
    *functions* is a list of strings.
    '''
    #data stores
    globals = []
    classes = []
    functions = []
    #rope stuff
    rope_project = project.Project(path_to_file)
    pyCore = pycore.PyCore(rope_project)
    module = pyCore.get_module(fileName)

    #Collect globals definitions!
    if module._get_structural_attributes().iteritems():
        for attr_name, attr in module._get_structural_attributes().iteritems():
            if isinstance(attr, AssignedName):
                lineno = attr.get_definition_location()[1]
                d_global = {'name': attr_name, 'lineno': lineno-1}
                globals.append(d_global)
    
    #This way I get only classes and functions defined in the file!
    if module._get_defined_objects():
        for obj in module._get_defined_objects():
            #this is a class!
            if isinstance(obj, AbstractClass):
                lineno = obj.get_scope().get_start()
                d = {'name': obj.get_name(), 'lineno': lineno-1, 'methods': [], 
                        'attributes':[], 'inside-classes':[],'superclasses': [] }
                #bases
                for klass in obj.get_superclasses():
                    if isinstance(klass, AbstractClass):
                        d['superclasses'].append(klass.get_name())
                
                #attributes
                for attr_name, attr in obj.get_attributes().iteritems():
                    if isinstance(attr, AssignedName):
                        #TRICK: Si el atributo pertenece al mismo modulo(archivo) que estoy analizando
                        #entonces podremos usar "go_to_line" sino lo descartamos
                        if attr.lineno and attr.module.get_resource().name[:-3] == fileName:
                            #lineno = obj[attr_name].get_definition_location()[1]
                            lineno = attr.lineno
                            d_attribute = {'name': attr_name, 'lineno': lineno-1}
                            d['attributes'].append(d_attribute)
                    #methods
                    elif isinstance(attr, DefinedName):
                        #Debe ser un metodo
                        if isinstance(attr.get_object(), AbstractFunction):
                            #TRICK: Si el metodo pertenece a la clase que estoy analizando
                            if attr.get_object().parent.get_name() == obj.get_name():
                                method_signature = create_signature(attr.get_object().get_name(), attr.get_object().get_param_names())
                                lineno = attr.get_object().get_scope().get_start()
                                d_method = {'name': method_signature, 'lineno': lineno-1}
                                d['methods'].append(d_method)
    
                #sort attributes and methods
                d['attributes'].sort(key=lambda d: d['name'])
                d['methods'].sort(key=lambda d: d['name'])
                #appent the class with attributes and methods
                classes.append(d)
            #this is a function!
            elif isinstance(obj, AbstractFunction):
                func_signature = create_signature(obj.get_name(), obj.get_param_names())
                lineno = obj.get_scope().get_start()
                d_function = {'name': func_signature, 'lineno': lineno-1}
                functions.append(d_function)

    #sort globals, classes and functions
    globals.sort(key=lambda d: d['name'])
    classes.sort(key=lambda d: d['name'])
    functions.sort(key=lambda d: d['name'])
    return (globals, classes, functions)


def debug(inspect_file_result):
    '''
    Function usefull for debugging the result of inspect_file
    '''
    globals = inspect_file_result[0]
    classes = inspect_file_result[1]
    functions = inspect_file_result[2]
    for klass in classes:
        print "Clase: %s(%s) %s" % (klass['name'], ', '.join([k for k in klass['superclasses']]), klass['lineno'])
    print
    print "Atributos"
    print "=========="
    for a in klass['attributes']:
        print a['name'], a['lineno']
    print
    print "Metodos"
    print "========"
    for m in klass['methods']:
        print m['name'], m['lineno']
    print
    print "Funciones"
    print "=========="
    for f in functions:
        print f['name'], f['lineno']
