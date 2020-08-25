import sys
import numpy as np
import imagej
from bfio.bfio import BioReader, BioWriter
import matplotlib.pyplot as plt

import bioformats
import javabridge as jutil
import argparse, logging, subprocess, time, multiprocessing, sys
from pathlib import Path

if __name__=="__main__":
    # Initialize the logger
    logging.basicConfig(format='%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger("new")
    logger.setLevel(logging.INFO)
    
    ''' Argument parsing '''
    logger.info("Parsing arguments...")
    parser = argparse.ArgumentParser(prog='main', description='Implementation of blurring plugin')
    
    # Input arguments
    parser.add_argument('--images', dest='images', type=str,
                        help='Input image collection to be processed by this plugin', required=True)
    
    # Output arguments
    parser.add_argument('--outDir', dest='outDir', type=str,
                        help='Output collection', required=True)
    
    # Parse the arguments
    args = parser.parse_args()
    images = args.images
    if (Path.is_dir(Path(args.images).joinpath('images'))):
        # switch to images folder if present
        fpath = str(Path(args.images).joinpath('images').absolute())
    logger.info('images = {}'.format(images))
    outDir = args.outDir
    logger.info('outDir = {}'.format(outDir))

    # Input and Output directories
    images = str(Path('.').joinpath('inputs').absolute())
    outDir = str(Path('.').joinpath('outputs').absolute())


    # Get all file names in images image collection
    images_files = [f.name for f in Path(images).iterdir() if f.is_file() and "".join(f.suffixes)=='.ome.tif']

    # Start ImageJ
    ij = imagej.init('sc.fiji:fiji')

    # Loop through files in images image collection and process
    for f in images_files:
        # Load an image
        br = BioReader(Path(images).joinpath(f))
        image = np.squeeze(br.read_image())

        # Create a RandomAccessibleInterval view for the image inside of ImageJ
        image_rai = ij.py.to_java(image)
        print("Image type (should be RandomAccesibleInterval): {}".format(type(image_rai).__name__))

        # Create the output numpy array
        output = np.zeros(image.shape,dtype=image.dtype)
        
        # Run the op
        ij.op().filter().gauss(ij.py.to_java(output),image_rai,10.0)
        
        plt.figure()
        plt.imshow(output)
        plt.show()
        plt.savefig(f[:-8]+"_IMAGE")
        
        output = np.reshape(output,(br.num_y(),br.num_x(),br.num_z(),1,1))
        
        # Display the original and processed images
        
        
        # Write the output
        bw = BioWriter(str(Path(outDir).joinpath(f)),image=output, metadata=br.read_metadata())
        bw.write_image(output)
        bw.close_image()
        
        
        
    
'''    
# Read an OME tiled tiff
br = BioReader('polus-plugins/inputs/r001_z000_y009_x012_c000.ome.tif')
image = br.read_image().squeeze() # squeeze to 2-dimensions



# Display the original and processed images
fig,ax = plt.subplots(1,2)
ax[0].imshow(image)
ax[1].imshow(output)
plt.show()
plt.savefig('bioreader11.png')
'''