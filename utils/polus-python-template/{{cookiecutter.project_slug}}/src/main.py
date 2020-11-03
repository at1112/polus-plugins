{% if cookiecutter.use_bfio -%}
from bfio.bfio import BioReader, BioWriter
import imagej
import bioformats
import javabridge as jutil
{%- endif %}
import argparse, logging, subprocess, time, multiprocessing, sys
import numpy as np
import imagej
import sys
from pathlib import Path
import matplotlib.pyplot as plt



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

    {% for inp,val in cookiecutter._inputs|dictsort -%}
    {% if val.type=="collection" -%}
    # Get all file names in {{ inp }} image collection
    {{ inp }}_files = [f.name for f in Path({{ inp }}).iterdir() if f.is_file() and "".join(f.suffixes)=='.ome.tif']
    {% endif %}
    {% endfor -%}

    # Start ImageJ
    ij = imagej.init('sc.fiji:fiji')

    {% for inp,val in cookiecutter._inputs|dictsort -%}
    {% for out,n in cookiecutter._outputs|dictsort -%}
    {% if val.type=="collection" and cookiecutter.use_bfio -%}



    # Loop through files in {{ inp }} image collection and process
    for f in {{ inp }}_files:
        # Load an image
        br = BioReader(Path({{ inp }}).joinpath(f))
        image = np.squeeze(br.read_image())

        # Create a RandomAccessibleInterval view for the image inside of ImageJ
        image_rai = ij.py.to_java(image)
        print("Image type (should be RandomAccesibleInterval): {}".format(type(image_rai).__name__))

        # Create the output numpy array
        output = np.zeros(image.shape,dtype=image.dtype)


        ###IF METHOD = SINGLE SIGMA, DO THIS:
        #defaultGaussRAISingleSigma

        ##get sigma arg for SINGLE RA
        {% for inp,val in cookiecutter._inputs|dictsort -%}
        {% if val =="sigma" -%}
        sigma = val
        {% endif %}
        {% endfor -%}


        ij.op().{{ cookiecutter.plugin_group }}.{{ cookiecutter.plugin_subgroup }}(ij.py.to_java(output),image_rai, float(sigma))


        {% for inp,val in cookiecutter._inputs|dictsort -%}
            {% for key2, nested_value in cookiecutter._inputs.items.items() %}
        {% if val =="DefaultGaussRA" -%}
        sigma = val
        {% endif %}
        {% endfor -%}

        ###ELSE IF METHOD = ARRAY OF SIGMA 1 or 2, DO THIS:
        #defaultGaussRA or defaultGaussRAI
        {% for inp,val in cookiecutter._inputs|dictsort -%}
        {% if val =="sigma_array" -%}
        for sigma in val:
             ij.op().{{ cookiecutter.plugin_group }}.{{ cookiecutter.plugin_subgroup }}(ij.py.to_java(output),image_rai, float(sigma))
        {% endif %}
        {% endfor -%}
 
       

        output = np.reshape(output,(br.num_y(),br.num_x(),br.num_z(),1,1))

        ##ELSE IF METHOD = EITHER OF THE 2 SIGMA ARRAY METHODS, DO THIS:

       



        # Write the output
        bw = BioWriter(str(Path({{ out }}).joinpath(f)),image=output, metadata=br.read_metadata())
        bw.write_image(output)
        bw.close_image()

        out = np.squeeze(output) # squeeze to 2-dimensions
        fig,ax = plt.subplots(1,2)
        #ax[0].imshow(image)
        ax[1].imshow(out)
        plt.show()
        plt.savefig('auto.png')     
    {%- endif %}{% endfor %}{% endfor %}


        
 
 
    