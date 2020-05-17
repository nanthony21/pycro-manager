import typing

import numpy as np

NewConnectionMsg = typing.TypedDict('NewConnectionMsg', {
    'type': str,
    'version': str
})

MethodSpec = typing.TypedDict('MethodSpecs', {
    'arguments': typing.List[str],
    'name': str,
    'return-type': str
})

SerializedObject = typing.TypedDict('SerializedObject', {
    "type": str,  # Should be "unserialized-object"
    'class': str,
    'fields': typing.List[str],
    'api': typing.List[MethodSpec],
    'hashcode': int,
    'interfaces': typing.List[str]
})

BasicSerializedObject = typing.TypedDict('BasicSerializedObject', {
    'type': str,
    'value': typing.Any
})

# CommandMsg = typing.TypedDict("CommandMsg", {
#     'command': str,
#     'classpath': str,
#     'argument-types': str,
#     'arguments': str,
#     'new-port': bool
#     },
# total=False)
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