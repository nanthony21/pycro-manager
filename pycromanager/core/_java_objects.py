from __future__ import annotations
import inspect
import json
import re
import typing
from base64 import standard_b64encode, standard_b64decode

import numpy as np

from . import _JAVA_TYPE_NAME_TO_PYTHON_TYPE, Bridge, _ARRAY_TYPE_TO_NUMPY_DTYPE, _CLASS_NAME_MAPPING


class JavaClassFactory:
    """
    This class is responsible for generating subclasses of JavaObjectShadow. Each generated class is kept in a `dict`.
    If a given class has already been generate once it will be returns from the cache rather than re-generating it.
    """
    def __init__(self):
        self.classes = {}

    def create(self, serialized_obj: dict, convert_camel_case: bool = True) -> typing.Type[JavaObjectShadow]:
        """Create a class (or return a class from the cache) based on the contents of `serialized_object` message."""
        if serialized_obj['class'] in self.classes.keys():  # Return a cached class
            return self.classes[serialized_obj['class']]
        else:  # Generate a new class since it wasn't found in the cache.
            _java_class: str = serialized_obj['class']
            python_class_name_translation = _java_class.replace('.', '_')  # Having periods in the name would be problematic.
            _interfaces = serialized_obj['interfaces']
            static_attributes = {'_java_class': _java_class, '_interfaces': _interfaces}

            fields = {}  # Create a dict of field names with getter and setter funcs.
            for field in serialized_obj['fields']:
                getter = lambda instance: instance._access_field(field)
                setter = lambda instance, val: instance._set_field(field, val)
                fields[field] = property(fget=getter, fset=setter)

            methods = {}  # Create a dict of methods for the class by name.
            methodSpecs = serialized_obj['api']
            method_names = set([m['name'] for m in methodSpecs])
            # parse method descriptions to make python stand ins
            for method_name in method_names:
                params, methods_with_name, method_name_modified = _parse_arg_names(methodSpecs, method_name, convert_camel_case)
                return_type = methods_with_name[0]['return-type']
                fn = lambda instance, *args, signatures_list=tuple(methods_with_name): instance._translate_call(signatures_list, args)
                fn.__name__ = method_name_modified
                fn.__doc__ = "{}.{}: A dynamically generated Java method.".format(_java_class, method_name_modified)
                sig = inspect.signature(fn)
                params = [inspect.Parameter('self', inspect.Parameter.POSITIONAL_ONLY)] + params  # Add `self` as the first argument.
                return_type = _JAVA_TYPE_NAME_TO_PYTHON_TYPE[return_type] if return_type in _JAVA_TYPE_NAME_TO_PYTHON_TYPE else return_type
                fn.__signature__ = sig.replace(parameters=params, return_annotation=return_type)
                methods[method_name_modified] = fn

            newclass = type(  # Dynamically create a class to shadow a java class.
                python_class_name_translation,  # Name, based on the original java name
                (JavaObjectShadow,),  # Inheritance
                {'__init__': lambda instance, socket, serialized_object, bridge: JavaObjectShadow.__init__(instance, socket, serialized_object, bridge),
                 **static_attributes, **fields, **methods}
            )

            self.classes[_java_class] = newclass
            print(f'created {newclass.__name__}')
            return newclass


class JavaObjectShadow:
    """
    Generic class for serving as a python interface for a micromanager class using a zmq server backend
    """
    _interfaces = None  # Subclasses should fill these out. This class should never be directly instantiated.
    _java_class = None

    def __init__(self, socket, serialized_object, bridge: Bridge):
        self._socket = socket
        self._hash_code = serialized_object['hash-code']
        self._bridge = bridge

    def __del__(self):
        """
        Tell java side this object is garbage collected so it can do the same if needed
        :return:
        """
        if not hasattr(self, '_hash_code'):
            return #constructor didnt properly finish, nothing to clean up on java side
        message = {'command': 'destructor', 'hash-code': self._hash_code}
        self._socket.send(message)
        reply_json = self._socket.receive()
        if reply_json['type'] == 'exception':
            raise Exception(reply_json['value'])

    def _access_field(self, name):
        """
        Return a python version of the field with a given name
        :return:
        """
        message = {'command': 'get-field', 'hash-code': self._hash_code, 'name': name}
        self._socket.send(message)
        return self._deserialize(self._socket.receive())

    def _set_field(self, name, value):
        """
        Return a python version of the field with a given name
        :return:
        """
        message = {'command': 'set-field', 'hash-code': self._hash_code, 'name': name, 'value': _serialize_arg(value)}
        self._socket.send(message)
        reply = self._deserialize(self._socket.receive())

    def _translate_call(self, method_specs, fn_args: tuple):
        """
        Translate to appropriate Java method, call it, and return converted python version of its result
        :param args: args[0] is list of dictionaries of possible method specifications
        :param kwargs: hold possible polymorphic args, or none
        :return:
        """
        #args that are none are placeholders to allow for polymorphism and not considered part of the spec
        fn_args = [a for a in fn_args if a is not None]
        valid_method_spec = _check_method_args(method_specs, fn_args)
        #args are good, make call through socket, casting the correct type if needed (e.g. int to float)
        message = {'command': 'run-method', 'hash-code': self._hash_code, 'name': valid_method_spec['name'],
                   'argument-types': valid_method_spec['arguments']}
        message['arguments'] = _package_arguments(valid_method_spec, fn_args)

        self._socket.send(message)
        return self._deserialize(self._socket.receive())

    def _deserialize(self, json_return):
        """
        :param method_spec: info about the method that called it
        :param reply: bytes that represents return
        :return: an appropriate python type of the converted value
        """
        if json_return['type'] == 'exception':
            raise Exception(json_return['value'])
        elif json_return['type'] == 'null':
            return None
        elif json_return['type'] == 'primitive':
            return json_return['value']
        elif json_return['type'] == 'string':
            return json_return['value']
        elif json_return['type'] == 'list':
            return [self._deserialize(obj) for obj in json_return['value']]
        elif json_return['type'] == 'object':
            if json_return['class'] == 'JSONObject':
                return json.loads(json_return['value'])
            else:
                raise Exception('Unrecognized return class')
        elif json_return['type'] == 'unserialized-object':
            #inherit socket from parent object
            return self._bridge.get_class(json_return)(socket=self._socket, serialized_object=json_return, bridge=self._bridge)
        else:
            return deserialize_array(json_return)


def serialize_array(array):
    return standard_b64encode(array.tobytes()).decode('utf-8')


def deserialize_array(json_return):
    """
    Convert a serialized java array to the appropriate numpy type
    :param json_return:
    :return:
    """
    if json_return['type'] == 'byte-array':
        return np.frombuffer(standard_b64decode(json_return['value']), dtype='>u1').copy()
    elif json_return['type'] == 'double-array':
        return np.frombuffer(standard_b64decode(json_return['value']), dtype='>f8').copy()
    elif json_return['type'] == 'int-array':
        return np.frombuffer(standard_b64decode(json_return['value']), dtype='>u4').copy()
    elif json_return['type'] == 'short-array':
        return np.frombuffer(standard_b64decode(json_return['value']), dtype='>u2').copy()
    elif json_return['type'] == 'float-array':
        return np.frombuffer(standard_b64decode(json_return['value']), dtype='>f4').copy()


def _package_arguments(valid_method_spec, fn_args):
    """
    Serialize function arguments and also include description of their Java types
    :param valid_method_spec:
    :param fn_args:
    :return:
    """
    arguments = []
    for arg_type, arg_val in zip(valid_method_spec['arguments'], fn_args):
        if isinstance(arg_val, JavaObjectShadow):
            arguments.append(_serialize_arg(arg_val))
        else:
            arguments.append(_serialize_arg(_JAVA_TYPE_NAME_TO_PYTHON_TYPE[arg_type](arg_val)))
    return arguments


def _serialize_arg(arg):
    if type(arg) in [bool, str, int, float]:
        return arg #json handles serialization
    elif type(arg) == np.ndarray:
        return serialize_array(arg)
    elif isinstance(arg, JavaObjectShadow):
        return {'hash-code': arg._hash_code}
    else:
        raise Exception('Unknown argumetn type')


def _check_method_args(method_specs, fn_args):
    """
    Compare python arguments to java arguments to find correct function to call
    :param method_specs:
    :param fn_args:
    :return: one of the method_specs that is valid
    """
    # TODO: check that args can be translated to expected java counterparts (e.g. numpy arrays)
    valid_method_spec = None
    for method_spec in method_specs:
        if len(method_spec['arguments']) != len(fn_args):
            continue
        valid_method_spec = method_spec
        for arg_type, arg_val in zip(method_spec['arguments'], fn_args):
            if isinstance(arg_val, JavaObjectShadow):
                if arg_type not in arg_val._interfaces:
                    # check that it shadows object of the correct type
                    valid_method_spec = None
            elif not isinstance(type(arg_val), type(_JAVA_TYPE_NAME_TO_PYTHON_TYPE[arg_type])):
                # if a type that gets converted
                valid_method_spec = None
            elif type(arg_val) == np.ndarray:
                # For ND Arrays, need to make sure data types match
                if _ARRAY_TYPE_TO_NUMPY_DTYPE[arg_type] != arg_val.dtype:
                    valid_method_spec = None
        # if valid_method_spec is None:
        #     break
    if valid_method_spec is None:
        raise Exception('Incorrect arguments. \nExpected {} \nGot {}'.format(
            ' or '.join([', '.join(method_spec['arguments']) for method_spec in method_specs]),
            ', '.join([str(type(a)) for a in fn_args]) ))
    return valid_method_spec


def _parse_arg_names(methods, method_name, convert_camel_case):
    method_name_modified = _camel_case_2_snake_case(method_name) if convert_camel_case else method_name
    # all methods with this name and different argument lists
    methods_with_name = [m for m in methods if m['name'] == method_name]
    min_required_args = 0 if len(methods_with_name) == 1 and len(methods_with_name[0]['arguments']) == 0 else \
        min([len(m['arguments']) for m in methods_with_name])
    # sort with largest number of args last so lambda at end gets max num args
    methods_with_name.sort(key=lambda val: len(val['arguments']))
    method = methods_with_name[-1]  # We only need to evaluate the overload with the most arguments.
    params = []
    unique_argument_names = []
    for arg_index, typ in enumerate(method['arguments']):
        hint = _CLASS_NAME_MAPPING[typ] if typ in _CLASS_NAME_MAPPING else 'object'
        python_type = _JAVA_TYPE_NAME_TO_PYTHON_TYPE[typ] if typ in _JAVA_TYPE_NAME_TO_PYTHON_TYPE else typ
        if hint in unique_argument_names:  # append numbers to end so arg hints have unique names
            i = 1
            while hint + str(i) in unique_argument_names:
                i += 1
            arg_name = hint + str(i)
        else:
            arg_name = hint
        unique_argument_names.append(arg_name)
        # this is how overloading is handled for now, by making default arguments as none, but
        # it might be better to explicitly compare argument types
        if arg_index >= min_required_args:
            default_arg_value = None
        else:
            default_arg_value = inspect.Parameter.empty
        params.append(inspect.Parameter(name=arg_name, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, default=default_arg_value, annotation=python_type))
    return params, methods_with_name, method_name_modified


def _camel_case_2_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()