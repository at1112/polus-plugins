from bfio.bfio import BioReader, BioWriter
import imagej
import bioformats
import javabridge as jutil
import argparse, logging, subprocess, time, multiprocessing, sys
import numpy as np
import imagej
import sys
from pathlib import Path
import matplotlib.pyplot as plt
from py4j.java_collections import SetConverter, MapConverter, ListConverter
from py4j.java_gateway import JavaGateway



if __name__=="__main__":
    # Initialize the logger
    logging.basicConfig(format='%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)

    ''' Argument parsing '''
    logger.info("Parsing arguments...")
    parser = argparse.ArgumentParser(prog='main', description='Automation of plugin creation for Gauss Single Sigma Filter Function')
    
    # Input arguments
    parser.add_argument('--inpDir', dest='inpDir', type=str,
                        help='Input image collection to be processed by this plugin', required=True)
    parser.add_argument('--method', dest='method', type=str,
                        help='method', required=True)
    parser.add_argument('--sigma', dest='sigma', type=str,
                        help='Constant sigma value', required=False)
    parser.add_argument('--sigma_array', dest='sigma_array', type=str,
                        help='Array of sigmas', required=False)
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
    sigma = args.sigma
    logger.info('sigma = {}'.format(sigma))
    sigma_array = args.sigma_array
    logger.info('sigma_array = {}'.format(sigma_array))
    method = args.method
    logger.info('method = {}'.format(method))
    outDir = args.outDir
    logger.info('outDir = {}'.format(outDir))

    

    # Get all file names in inpDir image collection
    inpDir_files = [f.name for f in Path(inpDir).iterdir() if f.is_file() and "".join(f.suffixes)=='.ome.tif']
    
    # Start ImageJ
    ij = imagej.init('sc.fiji:fiji')

    ##import things after imagej.init otherwise imagej doesn't work!!
    import imglyb
    from imglyb import util
    from jnius import JavaClass, MetaJavaClass, PythonJavaClass, java_method, autoclass, cast



    # Loop through files in inpDir image collection and process
    for f in inpDir_files:
        # Load an image
        br = BioReader(Path(inpDir).joinpath(f))
        image = np.squeeze(br.read_image())

        # Create a RandomAccessibleInterval view for the image inside of ImageJ
        image_rai = ij.py.to_java(image)
        print("Image type (should be RandomAccesibleInterval): {}".format(type(image_rai).__name__))

        # Create the output numpy array
        output = np.zeros(image.shape,dtype=image.dtype)

        
        jDouble = autoclass("java.lang.Double")
        jArray = autoclass("java.lang.reflect.Array")
        a = jArray.newInstance(jDouble, 2)
        

        #HelloWorld = autoclass('org.jnius.HelloWorld')
        #print HelloWorld().hello()
        #print(type(a))
        a[0] = jDouble(60.0)
        a[1] = jDouble(40.0)
        #print(type(a))

        b = ij.py.to_java(a)
        print(b)
        print(type(b))
        
        ij.op().filter().gauss(ij.py.to_java(output),image_rai, a)
        
        '''
        ##IF METHOD = DEFAULTGAUSSRA, SIGMA_ARRAY IS PROVIDED, WE RUN DEFAULTGAUSSRA
        if method is 'DefaultGaussRA' or 'DefaultGaussRAI':
            ij.op().filter().gauss(ij.py.to_java(output),image_rai, ij.py.to_java(a))

        else:
            ij.op().filter().gauss(ij.py.to_java(output),image_rai, float(sigma))

        '''
        output = np.reshape(output,(br.num_y(),br.num_x(),br.num_z(),1,1))

        # Write the outputs
        bw = BioWriter(str(Path(outDir).joinpath(f)),image=output, metadata=br.read_metadata())
        bw.write_image(output)
        bw.close_image()

        out = np.squeeze(output) # squeeze to 2-dimensions
        fig,ax = plt.subplots(1,2)
        #ax[0].imshow(image)
        ax[1].imshow(out)
        plt.show()
        plt.savefig('auto.png')


        
 
 
    