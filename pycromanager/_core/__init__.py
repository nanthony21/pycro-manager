from __future__ import annotations
import numpy as np
from ._bridge import Bridge
from ._java_objects import JavaObjectShadow

_CLASS_NAME_MAPPING = {'boolean': 'boolean', 'byte[]': 'uint8array',
                       'double': 'float', 'double[]': 'float64_array', 'float': 'float',
                       'int': 'int', 'int[]': 'uint32_array', 'java.lang.String': 'string',
                       'long': 'int', 'short': 'int', 'void': 'void',
                       'java.util.List': 'list'}
_ARRAY_TYPE_TO_NUMPY_DTYPE = {'byte[]': np.uint8, 'double[]': np.float64, 'int[]': np.int32}
_JAVA_TYPE_NAME_TO_PYTHON_TYPE = {'boolean': bool, 'byte[]': np.ndarray,
                                  'double': float, 'double[]': np.ndarray, 'float': float,
                                  'int': int, 'int[]': np.ndarray, 'java.lang.String': str,
                                  'long': int, 'short': int, 'char': int, 'byte': int, 'void': None}

__all__ = ['Bridge', 'JavaObjectShadow']

if __name__ == '__main__':
    #Test basic bridge operations
    import traceback
    b = Bridge()
    try:
        s = b.get_studio()
    except:
       traceback.print_exc()
    try:
        c = b.get_core()
    except:
        traceback.print_exc()
    a = 1
