from bfio.bfio import BioReader, BioWriter
import argparse, logging, sys
import numpy as np
from pathlib import Path
import ij_converter
import jpype
import imagej

if __name__=="__main__":
    # Initialize the logger
    logging.basicConfig(format='%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    
    # This is the version of ImageJ pre-downloaded into the docker container
    logger.info('Starting ImageJ...')
    ij = imagej.init("sc.fiji:fiji:2.1.1+net.imagej:imagej-legacy:0.37.4")
    ij_converter.ij = ij
    logger.info(ij.getVersion())

    ''' Setup Command Line Arguments '''
    logger.info("Parsing arguments...")
    parser = argparse.ArgumentParser(prog='main', description='{{ cookiecutter.project_short_description }}')
    
    # Input arguments
    {% for inp,val in cookiecutter._inputs.items() -%}
    parser.add_argument('--{{ inp }}', dest='{{ inp }}', type=str,
                        help='{{ val.description }}', required={{ val.required }})
    {% endfor %}
    # Output arguments
    {%- for out,val in cookiecutter._outputs.items() %}
    parser.add_argument('--{{ out }}', dest='{{ out }}', type=str,
                        help='{{ val.description }}', required=True)
    {% endfor %}
    """ Parse the arguments """
    args = parser.parse_args()
    
    # Input Args
    {%- for inp,val in cookiecutter._inputs.items() %}
    {% if val.type=="boolean" -%}
    _{{ inp }} = args.{{ inp }} == 'true'
    {% elif val.type=="collection" -%}
    _{{ inp }} = Path(args.{{ inp }})
    {% else -%}
    _{{ inp }} = args.{{ inp }}
    {% endif -%}
    logger.info('{{ inp }} = {}'.format(_{{ inp }}))
    {% endfor %}
    # Output Args
    {%- for out,val in cookiecutter._outputs.items() %}
    _{{ out }} = Path(args.{{ out }})
    logger.info('{{ out }} = {}'.format(_{{ out }}))
    {%- endfor %}
    
    """ Validate and organize the inputs """
    args = []
    arg_types = []
    arg_len = 0
    {% for inp,val in cookiecutter._inputs.items() %}
    # Validate {{ inp }}{% if inp != "opName" %}
    {{ inp }}_types = { {% for i,v in val.call_types.items() %}
        "{{ i }}": "{{ v }}",{% endfor %}
    }
      
    if _{{ inp }} == None and _opName in list({{ inp }}_types.keys()):
        raise ValueError('{} must be defined to run {}.'.format('{{ inp }}',_opName))
    elif _{{ inp }} != None:
    {%- if val.type == "collection" %}
        {{ inp }}_type = {{ inp }}_types[_opName]
    
        if _{{ inp }}.joinpath('images').is_dir():
            # switch to images folder if present
            _{{ inp }} = _{{ inp }}.joinpath('images').absolute()

        args.append([f for f in _{{ inp }}.iterdir() if f.is_file()])
        arg_len = len(args[-1])
    else:
        arg_types.append(None)
        args.append([None])
    {%- else %}
        {{ inp }} = ij_converter.to_java(_{{ inp }},{{ inp }}_types[_opName])
    else:
        {{ inp }} = None
    {%- endif %}
    {% else %}
    {{ inp }}_values = [{% for v in val.options %}
        "{{v}}",{% endfor %}
    ]
    assert _{{ inp }} in {{ inp }}_values, '{{ inp }} must be one of {}'.format({{ inp }}_values)
    {% endif %}{%- endfor %}
    for i in range(len(args)):
        if len(args[i]) == 1:
            args[i] = args[i] * arg_len
            
    """ Setup the output """
    {% for out,val in cookiecutter._outputs.items() %}
    {{ out }}_types = { {% for i,v in val.call_types.items() %}
        "{{ i }}": "{{ v }}",{% endfor %}
    }
    {%- endfor %}
    """ Run the plugin """
    try:
        for ind, (
            {%- for inp,val in cookiecutter._inputs.items() -%}
            {%- if val.type=='collection' %}{{ inp }}_path,{% endif -%}
            {%- endfor %}) in enumerate(zip(*args)):
            
            {%- for inp,val in cookiecutter._inputs.items() if val.type=='collection' %}
            {%- if val.type=='collection' %}
            if {{ inp }}_path != None:
                # Load the first plane of image in {{ inp }} collection
                logger.info('Processing image: {}'.format({{ inp }}_path))
                {{ inp }}_br = BioReader({{ inp }}_path)
                {{ inp }} = ij_converter.to_java(np.squeeze({{ inp }}_br[:,:,0:1,0,0]),{{ inp }}_type)
                {%- if loop.first %}
                metadata = {{ inp }}_br.metadata
                fname = {{ inp }}_path.name
                {%- endif %}
            {%- endif %}{% endfor %}

            logger.info('Running op...')
            {% for i,v in cookiecutter.plugin_namespace.items() %}
            {%- if loop.first %}if{% else %}elif{% endif %} _opName == "{{ i }}":
                {{ v }}
            {% endfor %}
            logger.info('Completed op!')
            
            {%- for inp,val in cookiecutter._inputs.items() %}
            {%- if val.type=='collection' %}
            if {{ inp }}_path != None:
                {{ inp }}_br.close()
            {%- endif %}{% endfor %}
            
            {% for out,val in cookiecutter._outputs.items() -%}
            # Save {{ out }}
            logger.info('Saving...')
            {{ out }}_array = ij_converter.from_java({{ out }},{{ out }}_types[_opName])
            bw = BioWriter(_{{ out }}.joinpath(fname),metadata=metadata)
            bw.Z = 1
            bw.dtype = {{ out }}_array.dtype
            bw[:] = {{ out }}_array
            bw.close()
            {%- endfor %}
            
    except:
        logger.error('There was an error, shutting down jvm before raising...')
        raise
            
    finally:
        # Exit the program
        logger.info('Shutting down jvm...')
        del ij
        jpype.shutdownJVM()
        logger.info('Complete!')