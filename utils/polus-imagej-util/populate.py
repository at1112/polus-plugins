'''

This script creates a nested dictionary containing the components of an ImageJ
function call. I have manually mapped some ImageJ datatypes to WIPP types, and
attempt to populate a cookiecutter.json from this formatted dictionary
iteratively.

'''
import re, json, pprint, logging, copy
from pathlib import Path
import imagej, scyjava

""" Parse ImageJ Op Metadata """
# Start PyImageJ
ij = imagej.init("sc.fiji:fiji:2.1.1+net.imagej:imagej-legacy:0.37.4",headless=True)

# Get a list of plugins related to ops
plugin_list = list(ij.op().ops().iterator())

# List of plugins to skip
skip_classes = [
    'copy',
    'create.img',
    'create.imgPlus'
]

# Get op subclass metadata
text = scyjava.to_python(ij.op().help())

""" Type Conversions """
# Values that map to collection
COLLECTION_TYPES = [
    'Iterable',
    'Interval',
    'IterableInterval',
    # 'IterableRegion',
    'RandomAccessibleInterval',
    'ImgPlus',
    'PlanarImg',
    # 'ImgFactory',
    # 'ImgLabeling',
    'ArrayImg',
    'Img'
]

# Values that map to number
NUMBER_TYPES = [
    'RealType',
    'NumericType',
    'byte', 'ByteType', 'UnsignedByteType',
    'short','ShortType','UnsignedShortType',
    'int','Integer','IntegerType',
    'long', 'Long', 'LongType', 'UnsignedLongType',
    'float','FloatType',
    'double','Double','DoubleType'
]

# Values that map to boolean
BOOLEAN_TYPES = [
    'boolean','Boolean','BooleanType'
]

# Values that map to array
ARRAY_TYPES = [
    # 'double[][]',
    'List',
    'double[]',
    'long[]',
    'ArrayList',
    # 'Object[]',
    'int[]'
]

# Values that map to string
STRING_TYPES = [
    'RealLocalizable',
    'String'
]

IMAGEJ_WIPP_TYPE = {t:'collection' for t in COLLECTION_TYPES}
IMAGEJ_WIPP_TYPE.update({t:'number' for t in NUMBER_TYPES})
IMAGEJ_WIPP_TYPE.update({t:'boolean' for t in BOOLEAN_TYPES})
IMAGEJ_WIPP_TYPE.update({t:'array' for t in ARRAY_TYPES})
IMAGEJ_WIPP_TYPE.update({t:'string' for t in STRING_TYPES})

""" Dictionaries to Generate Cookicutter JSON """
# Input variable dictionary
input_dict = {
    "type": None,
    "title": None,
    "description": None,
    "required": False,
    "call_types": {}
}

# Output variable dictionary
output_dict = {
    "type": "collection",
    "title": None,
    "description": None,
    "call_types": {}
}

# Separator between input/output variables
separator = ',\n'

# The core of the plugin json
plugin_template = {
    "author": "Anjali Taneja",
    "email": "Anjali.Taneja@axleinfo.com",
    "github_username": "at1112",
    "version": "0.1.1",
    "bfio_version": "2.0.0a4",
    "bfio_container": "imagej",
    
    "project_name": {},
    "project_short_description": {},
    
    "plugin_namespace": {},
    
    "_inputs": {},
    "_outputs": {},
    
    "project_slug": "polus-{{ cookiecutter.project_name|lower|replace(' ', '-') }}-plugin"
}
    
""" Parse the ImageJ ops help text """
# Remove white space characters
text = text.replace('\n','')
text = text.replace('\t','')
text = text.replace('=','= ')

# Loop variables
nested_dict = {}
keys=[]
Inputs = []
Outputs = []
count = 0

# Parse inputs/outputs
split_text = re.compile("([(][a-zA-Z0-9\][a-zA-Z]+[ ]+[a-z?]+[)]+[ ]+[=])+[ ]").split(text) #gets everything but the (RealType out? String errMsg)

# Loop through ImageJ Ops
for index,element in enumerate(split_text):
    z = re.match("(?:^|\W)net.imagej.ops.([a-z]+).([a-z0-9A-Z$]+).([a-z0-9A-Z$]+).([a-z0-9A-Z$]+).([a-zA-Z0-9]+)\(([\sa-zA-Z0-9,\[\]\?]*)\)", element)
    if z:
        match_string = z.group(0)
        keys.append(match_string.split('(')[0].split('.')[3:])
        
        output = split_text[index-1]
        outputs = output[1:-3]
        inputs = match_string.split('(')[1][:-1]
        inputs = inputs.split(',')
        
        for i,item in enumerate(inputs):
            if item.endswith(' in'):
                inputs[i] += '1'
        
        for i,item in enumerate(reversed(inputs)):
            if outputs in item:
                inputs.pop(len(inputs) - i - 1)
        
        Inputs.append(inputs)
        Outputs.append([outputs])
        
"""
Create a Java class dictionary with defined input/output type conversions

This code does two things:
1. Maps input/output data types between wipp and imagej
2. Skip any classes that do not have a wipp collection as either input or output

If a class doesn't have a collection as an input or output type, the
functionality will likely be limited from within WIPP. This may need to be
changed in the future. For example, if a plugin calculates the mean of an image
or calculates the mean of a region of interest, it will likely have image as an
input and a numeric or array type output that could be dumped into a csv.

Also, optional inputs are ignored at the moment. It may be desireable to find a
way to include them in the future.
"""
java_classes = {}
for index, path in enumerate(keys):
    class_name = path[-1]
    plugin_name = '.'.join(path[:-1])
    
    if plugin_name in skip_classes:
        continue
    
    outputs = {o.split(' ')[1].rstrip('?'):
                {'wipp_type': IMAGEJ_WIPP_TYPE.get(o.split(' ')[0]),
                 'imagej_type': o.split(' ')[0]} for o in Outputs[index]}
    
    if 'collection' not in [o['wipp_type'] for o in outputs.values()] or \
        None in [o['wipp_type'] for o in outputs.values()]:
        continue
    
    inputs = {i.split(' ')[1]:
                {'wipp_type': IMAGEJ_WIPP_TYPE.get(i.split(' ')[0]),
                 'imagej_type': i.split(' ')[0]} for i in Inputs[index] if not i.endswith('?')}
    
    if 'collection' not in [i['wipp_type'] for i in inputs.values()] or \
        None in [i['wipp_type'] for i in inputs.values()]:
        continue
    
    if plugin_name in java_classes.keys():
        java_classes[plugin_name].update({
            class_name: {
                '_inputs': inputs,
                '_outputs': outputs
            }
        })
    else:
        java_classes[plugin_name] = {
            class_name: {
                '_inputs': inputs,
                '_outputs': outputs
            }
        }

    
""" Build the cookiecutter dictionaries for each plugin

This section of code uses all the above information to build a dictionary that
can be exported as a cookiecutter json file. The Java classes found above are
grouped by the plugin
"""
plugins = {}
count = 0
for plugin_name,plugin_info in java_classes.items():
    
    # Initialize the plugin json from the template
    plugin_dict = copy.deepcopy(plugin_template)
    plugin_dict['project_name'] = 'ImageJ ' + plugin_name.replace('.', ' ')
    plugin_dict['project_short_description'] = ','.join(list(plugin_info.keys()))
    
    # Determine the root namespace
    root_namespace = 'ij.op('
    for name in plugin_name.split('.'):
        namespace = root_namespace + ')'
        if name not in dir(eval(namespace)):
            break
        root_namespace = namespace + '.' + name + '('
        
    # Determine the code to execute the op
    plugin_namespace = {}
    for op_name,op_info in plugin_info.items():
        
        try:
            namespace = root_namespace + ')'
            op_method = op_name.split('$')[-1][0].lower() + op_name.split('$')[-1][1:]
            if op_method in dir(eval(namespace)):
                plugin_namespace[op_name] = namespace + '.' + op_method + '('
            else:
                continue
        except:
            plugin_namespace[op_name] = root_namespace
        
        # Set the output
        plugin_namespace[op_name] = list(op_info['_outputs'].keys())[0] + ' = ' + plugin_namespace[op_name]
        
        # Set the inputs
        plugin_namespace[op_name] += ','.join(list(op_info['_inputs'].keys())) + ')'
        
    plugin_dict['plugin_namespace'] = plugin_namespace
    
    # Create an enum to select an op for the plugin
    inp = {
        "opName": {
            "title": "Operation",
            "type": "enum",
            "options": list(plugin_namespace.keys()),
            "description": "Operation to perform",
            "required": False
        }
    }
    
    # Define the inputs
    for key in plugin_namespace.keys():
        
        io = plugin_info[key]
        
        for input_name,type_dict in io['_inputs'].items():
            if input_name not in inp.keys():
                inp[input_name] = copy.deepcopy(input_dict)
                inp[input_name]['type'] = type_dict['wipp_type']
                inp[input_name]['title'] = input_name
                inp[input_name]['description'] = input_name
            
            inp[input_name]['call_types'][key] = type_dict['imagej_type']
    plugin_dict['_inputs'] = inp
    
    # Define the inputs
    out = {}
    for key in plugin_namespace.keys():
        
        io = plugin_info[key]
        
        for output_name,type_dict in io['_outputs'].items():
            if output_name not in out.keys():
                out[output_name] = copy.deepcopy(output_dict)
                out[output_name]['type'] = type_dict['wipp_type']
                out[output_name]['title'] = output_name
                out[output_name]['description'] = output_name
            
            out[output_name]['call_types'][key] = type_dict['imagej_type']
    plugin_dict['_outputs'] = out
    
    file_path = Path(__file__).with_name('cookietin').joinpath(plugin_name.replace('.','-'))
    file_path.mkdir(exist_ok=True,parents=True)
    
    with open(file_path.joinpath('cookiecutter.json'),'w') as fw:
        json.dump(plugin_dict,fw,indent=4)
