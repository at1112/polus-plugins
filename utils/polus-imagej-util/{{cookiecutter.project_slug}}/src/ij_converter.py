import imagej
import logging
import imglyb

# Initialize the logger
logging.basicConfig(format='%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger("ij_converter")
logger.setLevel(logging.INFO)

ij = None

def set_ij(ij_instance):
    global ij
    
    ij = ij_instance

def to_java(np_array,java_type):
    
    if ij == None:
        raise ValueError('No imagej instance found.')
    
    if java_type == 'IterableInterval' or java_type == 'Iterable':
        java_array = ij.py.to_java(np_array)
        out_array = imglyb.util.Views.iterable(java_array)
    elif java_type == 'RealType':
        out_array = imglyb.types.FloatType(float(np_array))
    else:
        logger.warning('Did not recognize type, {}, will pass default.'.format(java_type))
        out_array = ij.py.to_java(np_array)
    
    return out_array

def from_java(java_array,java_type):
    
    if ij == None:
        raise ValueError('No imagej instance found.')
    
    if ij.py.dtype(java_array) == bool:
        java_array = ij.op().convert().uint8(java_array)
    
    return ij.py.from_java(java_array)