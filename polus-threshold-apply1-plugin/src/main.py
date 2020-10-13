import sys
#import cv2
import traceback
import csv
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
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)

    ''' Argument parsing '''
    logger.info("Parsing arguments...")
    parser = argparse.ArgumentParser(prog='main', description='Automation of plugin creation for Threshold Apply functions')
    
    # Input arguments
    parser.add_argument('--inpDir', dest='inpDir', type=str,
                        help='Input image collection to be processed by this plugin', required=True)
    parser.add_argument('--threshVal', dest='threshVal', type=str,
                        help='Constant threshold value', required=True)
    # Output arguments
    parser.add_argument('--outDir', dest='outDir', type=str,
                        help='Output collection', required=True)
    
    
    
    
    # Parse the arguments
    args = parser.parse_args()
    inpDir = args.inpDir
    if (Path.is_dir(Path(args.inpDir).joinpath('images'))):
            
        # switch to images folder if present
        fpath = str(Path(args.inpDir).joinpath('images').absolute())
            
    logger.info('inpDir = {}'.format(inpDir))
    threshVal = args.threshVal
    logger.info('threshVal = {}'.format(threshVal))
    outDir = args.outDir
    logger.info('outDir = {}'.format(outDir))
        

            
     # Get all file names in images image collection
    images_files = [f.name for f in Path(inpDir).iterdir() if f.is_file() and "".join(f.suffixes)=='.ome.tif']

    # Start ImageJ
    ij = imagej.init('sc.fiji:fiji')

    ##import things after imagej.init otherwise imagej doesn't work!!
    import imglyb
    from imglyb import util
    from jnius import JavaClass, MetaJavaClass, PythonJavaClass, java_method, autoclass, cast


    # Loop through files in images image collection and process
    for f in images_files:
        # Load an image
        br = BioReader(Path(inpDir).joinpath(f))
        a = br.read_image(X=(0,256),Y=(0,256))
        #a = br.read_image()
        #print(a)        
        image = np.squeeze(a)

        # Create a RandomAccessibleInterval view for the image inside of ImageJ
        image_rai = ij.py.to_java(image)
        print("Image type (should be RandomAccesibleInterval): {}".format(type(image_rai).__name__))

        # Create the output numpy array
        output = np.zeros(image.shape,dtype=image.dtype)

        ##Transform image and output into IterableInterval
        arg_out = ij.op().transform().flatIterableView(ij.py.to_java(output))
        arg_in = ij.op().transform().flatIterableView(image_rai)

        ##Access UnsignedShorterType class
        UnsignedShorterType = autoclass('net.imglib2.type.numeric.integer.UnsignedShortType')
        thresh_val = UnsignedShorterType()
        thresh_val.set(float(threshVal))

        ##Call Threshold.Apply function
        output = ij.op().threshold().apply(arg_in, thresh_val)

        ##see type and features of output
        print('type(output): {}'.format(type(output)))
        print('dir(output): {}'.format(dir(output)))

        #create cursor object
        cursor = output.cursor()
        print(dir(cursor))

        print(output.size())

        output_np = np.zeros(((256,256,1,1,1)),dtype=image.dtype)
        #output_np = np.zeros(((image.shape[0],image.shape[1],1,1,1)),dtype=image.dtype)
        
        for x in range(256):
        #for x in range(image.shape[1]):
            
            for y in range(256):
            #for y in range(image.shape[0]):
                
                output_np[y,x,0,0,0] = np.uint8(cursor.next().toString())

        unique, counts = np.unique(output_np, return_counts=True)
        print(dict(zip(unique, counts)))
         
        #print(output_np)     
        plt.imshow(output_np[:,:,0,0,0])
        plt.savefig('test.png')

        #output = np.reshape(output_np,(br.num_y(),br.num_x(),br.num_z(),1,1))

            
        # Write the output
        bw = BioWriter(str(Path(outDir).joinpath(f)),image=output_np, metadata=br.read_metadata())
        bw.write_image(output_np)
        bw.close_image()
        
        
    
'''           
# Read an OME tiled tiff
br = BioReader('INP1/r001_z000_y009_x012_c000.ome.tif')
image = np.squeeze(br.read_image(X=(0,256),Y=(0,256))) # squeeze to 2-dimensions
Two_out = np.squeeze(output_np)


# Display the original and processed images
fig,ax = plt.subplots(1,2)
ax[0].imshow(image)
ax[1].imshow(Two_out)
plt.show()
plt.savefig('converted1.png')
'''


