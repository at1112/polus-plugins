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
print(nested_dict['threshold']['apply']['ApplyConstantThreshold']['Input'][1][1])

#ij.op().filter.gauss(ij.py.to_java(nested_dict['filter']['gauss']['GaussRAISingleSigma']['Output'][0][0]), nested_dict['filter']['gauss']['GaussRAISingleSigma']['Input'][0][0], nested_dict['filter']['gauss']['GaussRAISingleSigma']['Input'][1][0]))

my_dictionary = {
    "author": "Anjali Taneja",
    "email": "Anjali.Taneja@axleinfo.com",
    "github_username": "at1112",
    "project_name": "Threshold Apply1",
    "project_short_description": "Automation of plugin creation for Threshold Apply functions",
    "version": "0.1.1",
    "use_bfio": "True",
    "plugin_name": "Filter Gauss",
    "plugin_group": "filter()",
    "plugin_subgroup": "gauss()",
    
    "_inputs": {
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
            "required": "True"
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