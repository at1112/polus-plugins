'''

This script creates a nested dictionary containing the components of an ImageJ function call. 
I have manually mapped some ImageJ datatypes to WIPP types, and attempt to populate a cookiecutter.json
from this formatted dictionary iteratively

'''
import re
import json
import sys
import numpy as np
import imagej
from bfio.bfio import BioReader, BioWriter
import matplotlib.pyplot as plt
import bioformats
import javabridge as jutil
import argparse, logging, subprocess, time, multiprocessing, sys
from pathlib import Path


f = open("output.txt")
text = f.read()
f.close()
text = text.replace('\n','')
text = text.replace('\t','')
text = text.replace('=','= ')
split_text = re.compile("([(][a-zA-Z0-9\][a-zA-Z]+[ ]+[a-z?]+[)]+[ ]+[=])+[ ]").split(text) #gets everything but the (RealType out? String errMsg)
list2 = []
nested_dict = {}
count= 0
nested_dict = {}
keys=[]
Inputs = []
Outputs = []
for index,element in enumerate(split_text):
    count += 1
    z = re.match("(?:^|\W)net.imagej.ops.([a-z]+).([a-z0-9A-Z$]+).([a-z0-9A-Z$]+).([a-z0-9A-Z$]+).([a-zA-Z0-9]+)\(([\sa-zA-Z0-9,\[\]\?]*)\)", element)
    if z:
        match_string = z.group(0)
        keys.append(match_string.split('(')[0].split('.')[3:])
        
        output = split_text[index-1]
        outputs = output[1:].split(' ')[0]
        inputs = match_string.split('(')[1][:-1]
        inputs = inputs.split(',')
        Inputs.append(inputs)
        for i,item in enumerate(inputs):
            if outputs in item:
                inputs.pop(i)
        Outputs.append([outputs])
        #print(inputs)
        #print(outputs)
        #print(match_string)
for index, path in enumerate(keys):
    for i in range(2):
        if i == 0:
            path.append('Input')
            path.append(Inputs[index])
            
            
            path[-1] = [[k, 0] for k in path[-1]]
            length = len(path[-1])

            ##Here, I map IJ types to WIPP types

            for i in range(length):
                
                ##MAP COLLECTIONS!!
                if 'Interval' in path[-1][i][0] or 'Iterable' in path[-1][i][0]:
                    path[-1][i][1] = 'collection'
                    
                ##MAP NUMBERS!!
                if 'Integer' in path[-1][i][0] or 'RealType' in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'int' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'double' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'Double' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'NumericType' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'long' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'Long' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'float' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'Float' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'short' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'Short' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                    path[-1][i][1] = 'number'
                if 'byte' in path[-1][i][0] or 'Byte' in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                
                ##MAP STRINGS!!
                if 'ComplexType' in path[-1][i][0]:
                    path[-1][i][1] = 'string'
                    
                ##MAP BOOLEANS!!
                if 'Boolean' in path[-1][i][0] or 'boolean' in path[-1][i][0]:
                    path[-1][i][1] = 'boolean'
                
                ####MAP ARRAYS!!
                if '[]' in path[-1][i][0] or 'List' in path[-1][i][0]:
                    path[-1][i][1] = 'array'
                    
            
        else:
            path[-2] = 'Output'
            path[-1] = Outputs[index]
            
            path[-1] = [[k, 0] for k in path[-1]]
            
        
            
        current_level = nested_dict
        
        
        for part in path:
            if part not in current_level:
                if part == 'Input':
                    current_level[part] = path[-1]
                    break
                elif part == 'Output':
                    current_level[part] = path[-1]
                    
                    
                    length = len(path[-1])
                    
                    ##Here, I map IJ types to WIPP types

                    for i in range(length):
                        
                        #map numbers

                        if 'Integer' in path[-1][i][0] or 'RealType' in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'int' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'double' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'Double' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'NumericType' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'long' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'Long' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'Float' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'float' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'short' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'Short' in path[-1][i][0] and '[]' not in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                        if 'byte' in path[-1][i][0] or 'Byte' in path[-1][i][0]:
                            path[-1][i][1] = 'number'
                            
                        ##MAP COLLECTIONS!!
                        if 'Interval' in path[-1][i][0] or 'Iterable' in path[-1][i][0]:
                            path[-1][i][1] = 'collection'
                        if 'Img' in path[-1][i][0]:
                            path[-1][i][1] = 'collection'
                            
                        ##MAP BOOLEANS!!
                        if 'Boolean' in path[-1][i][0] or 'boolean' in path[-1][i][0]:
                            path[-1][i][1] = 'boolean'
                            
                        ##MAP STRINGS!!
                        if 'Localizable' in path[-1][i][0]:
                            path[-1][i][1] = 'string'
                        if 'String' in path[-1][i][0]:
                            path[-1][i][1] = 'string'
                            
                        ####MAP ARRAYS!!
                        if '[]' in path[-1][i][0] or 'List' in path[-1][i][0]:
                            path[-1][i][1] = 'array'
                            
                    #print(path[-1])
                    break
                else:
                    current_level[part] = {}
            current_level = current_level[part]

#print(nested_dict['threshold']['apply']['ApplyConstantThreshold'])   

##STORES ALL GROUP NAMES IN LIST:
a = list(nested_dict.keys())
print(type(a))
print(a)


##Can use this if we want each plugin to work for a group, but makes more sense to do it for subgroups (e.g. not "project_name:Threshold" but "project_name:Threshold-Apply")
for item in a:
    my_dictionary = {
        "author": "Anjali Taneja",
        "email": "Anjali.Taneja@axleinfo.com",
        "github_username": "at1112",
        "project_name": item 
    }
    print(my_dictionary)


##This Recursive function prints all of the components in order! How to parse through this to fill a .json?
def recursive_items(dictionary):
    for key, value in dictionary.items():
        submodules = []
        if type(value) is dict:
            print (key)
            yield from recursive_items(value)
        else:
            yield (key, value)

for key, value in recursive_items(nested_dict):
    print(key, value)



'''
def iterdict(d):
    submodules = []
    for k,v in d.items():
        if isinstance(v, dict) and v != 'Inputs':
            submodules.append(k)
            iterdict(v)
        else:       
            submodules.append(k)    
            inputs = k['Inputs']
            outputs = k['Outputs']
    return submodules, inputs, outputs
'''



##This nests all the way into the dict until you get inputs/outputs:
def iterdict(d):
    for k,v in d.items():        
        if isinstance(v, dict):
            iterdict(v)
        else:            
            print (k,":",v)

iterdict(nested_dict)


##I can use this with indexing through a dict one function or one group at a time (but want to automate):
##feel free to comment this out, this is what I use to create the .jsons one at a time-

my_dictionary = {
    "author": "Anjali Taneja",
    "email": "Anjali.Taneja@axleinfo.com",
    "github_username": "at1112",
    "project_name": "Threshold Apply All",
    "project_short_description": "Automation of plugin creation for ALL Threshold Apply functions",
    "version": "0.1.1",
    "use_bfio": "True",
    "plugin_name": "Filter Gauss",
    "plugin_group": "filter()",
    "plugin_subgroup": "gauss()",
    
    "_inputs": {
        "method": {
            "type": "enum",
            "title": "filter gauss type",
            "description": "select the type of filter",
            "options": {
                "values": [
                    nested_dict['filter']['gauss'],
                    "GaussRAISingleSigma",
                    "DefaultGaussRAI"
                ]
            },
            "required": "True"
        },
        "inpDir": {
            "type": nested_dict['filter']['gauss']['GaussRAISingleSigma']['Input'][0][1],
            "title": nested_dict['filter']['gauss']['GaussRAISingleSigma']['Input'][0][0],
            "description": "Input image collection to be processed by this plugin",
            "required": "True"
        },
        "sigma": {
            "type": nested_dict['filter']['gauss']['GaussRAISingleSigma']['Input'][1][1],
            "title": nested_dict['filter']['gauss']['GaussRAISingleSigma']['Input'][1][0],
            "description": "Constant threshold value",
            "required": "False"
          },
        "sigma_array": {
            "type": "array",
            "title": "RealType in2",
            "description": "Array of sigma values",
            "required": "False"
        }
    },
    "_outputs": {
        "outDir": {
            "type": nested_dict['filter']['gauss']['GaussRAISingleSigma']['Output'][0][1],
            "description": "Output collection"
        }
    },
    
    "project_slug": "polus-{{ cookiecutter.project_name|lower|replace(' ', '-') }}-plugin"
}


with open('cookiecutter.json', 'w+') as f:
    # this would place the entire output on one line
    # use json.dump(lista_items, f, indent=4) to "pretty-print" with four spaces per indent
    json.dump(my_dictionary, f, indent=4)
