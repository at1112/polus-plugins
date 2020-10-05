{% if cookiecutter.use_bfio -%}
from bfio.bfio import BioReader, BioWriter
import bioformats
import javabridge as jutil
{%- endif %}
import argparse, logging, subprocess, time, multiprocessing, sys
import numpy as np
from pathlib import Path

if __name__=="__main__":
    # Initialize the logger
    logging.basicConfig(format='%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)

    ''' Argument parsing '''
    logger.info("Parsing arguments...")
    parser = argparse.ArgumentParser(prog='main', description='{{ cookiecutter.project_short_description }}')
    
    # Input arguments
    {% for inp,val in cookiecutter._inputs|dictsort -%}
    parser.add_argument('--{{ inp }}', dest='{{ inp }}', type=str,
                        help='{{ val.description }}', required={{ val.required }})
    {% endfor -%}
    
    # Output arguments
    {%- for out,val in cookiecutter._outputs|dictsort %}
    parser.add_argument('--{{ out }}', dest='{{ out }}', type=str,
                        help='{{ val.description }}', required=True)
    {% endfor %}
    
    
    # Parse the arguments
    args = parser.parse_args()
    {% for inp,val in cookiecutter._inputs|dictsort -%}
    {% if val.type=="boolean" -%}
    {{ inp }} = args.{{ inp }} == 'true'
    logger.info('{{ inp }} = {}'.format({{ inp }}))
    {% else -%}
    {{ inp }} = args.{{ inp }}
    {% if val.type=="collection" and cookiecutter.use_bfio -%}
    if (Path.is_dir(Path(args.{{ inp }}).joinpath('images'))):
        
        # switch to images folder if present
        fpath = str(Path(args.{{ inp }}).joinpath('images').absolute())
        
    {% endif -%}
    logger.info('{{ inp }} = {}'.format({{ inp }}))
    {% endif -%}
    {% endfor %}
    {%- for out,val in cookiecutter._outputs|dictsort -%}
    {{ out }} = args.{{ out }}
    logger.info('{{ out }} = {}'.format({{ out }}))
    {%- endfor %}
    
    # Surround with try/finally for proper error catching
    try:
        {% if cookiecutter.use_bfio -%}
        # Start the javabridge with proper java logging
        logger.info('Initializing the javabridge...')
        log_config = Path(__file__).parent.joinpath("log4j.properties")
        jutil.start_vm(args=["-Dlog4j.configuration=file:{}".format(str(log_config.absolute()))],class_path=bioformats.JARS)
        {% endif -%}
        {% for inp,val in cookiecutter._inputs|dictsort -%}
        {% if val.type=="collection" -%}
        # Get all file names in {{ inp }} image collection
        {{ inp }}_files = [f.name for f in Path({{ inp }}).iterdir() if f.is_file() and "".join(f.suffixes)=='.ome.tif']
        {% endif %}
        {% endfor -%}
        {% for inp,val in cookiecutter._inputs|dictsort -%}
        {% for out,n in cookiecutter._outputs|dictsort -%}
        {% if val.type=="collection" and cookiecutter.use_bfio -%}
        
        
        
        ##Loop through files
        
        # Get all file names in images image collection
        images_files = [f.name for f in Path(inpDir).iterdir() if f.is_file() and "".join(f.suffixes)=='.ome.tif']

        # Start ImageJ
        ij = imagej.init('sc.fiji:fiji')
        
        # Loop through files in images image collection and process
        for f in images_files:
            # Load an image
            br = BioReader(Path(inpDir).joinpath(f))
            image = np.squeeze(br.read_image())

            # Create a RandomAccessibleInterval view for the image inside of ImageJ
            image_rai = ij.py.to_java(image)
            print("Image type (should be RandomAccesibleInterval): {}".format(type(image_rai).__name__))

            # Create the output numpy array
            output = np.zeros(image.shape,dtype=image.dtype)
            
            # Run the op
            ij.op().filter().gauss(ij.py.to_java(output),image_rai, 10.0)
            
            #ij.op().filter().gauss(ij.py.to_java(output),image_rai, float(threshVal))
            
            
            #{% for thing in cookiecutter._plugin_group|dictsort -%}
            
            
            output = np.reshape(output,(br.num_y(),br.num_x(),br.num_z(),1,1))
            
            
            # Write the output
            bw = BioWriter(str(Path(outDir).joinpath(f)),image=output, metadata=br.read_metadata())
            bw.write_image(output)
            bw.close_image()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # Loop through files in {{ inp }} image collection and process
        for i,f in enumerate({{ inp }}_files):
            # Load an image
            br = BioReader(Path({{ inp }}).joinpath(f))
            image = np.squeeze(br.read_image())

            # initialize the output
            out_image = np.zeros(image.shape,dtype=br._pix['type'])

            """ Do some math and science - you should replace this """
            logger.info('Processing image ({}/{}): {}'.format(i,len({{ inp }}_files),f))
            out_image = awesome_math_and_science_function(image)

            # Write the output
            bw = BioWriter(Path({{ out }}).joinpath(f),metadata=br.read_metadata())
            bw.write_image(np.reshape(out_image,(br.num_y(),br.num_x(),br.num_z(),1,1)))
        {%- endif %}{% endfor %}{% endfor %}
        
    finally:
        {%- if cookiecutter.use_bfio %}
        # Close the javabridge regardless of successful completion
        logger.info('Closing the javabridge')
        jutil.kill_vm()
        {%- endif %}
        
        # Exit the program
        sys.exit()