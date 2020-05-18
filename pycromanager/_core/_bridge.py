from __future__ import annotations
import json
import time
import typing
import warnings

import numpy as np
import zmq

from ._java_objects import JavaClassFactory, _package_arguments, _check_method_args
from pycromanager import JavaObjectShadow


class Bridge:
    """
    Create an object which acts as a client to a corresponding server running within micro-manager.
    This enables construction and interaction with arbitrary java objects
    """
    _DEFAULT_PORT = 4827
    _EXPECTED_ZMQ_SERVER_VERSION = '2.5.0'

    def __init__(self, port=_DEFAULT_PORT, convert_camel_case=True, debug=False):
        """
        :param port: The port on which the bridge operates
        :type port: int
        :param convert_camel_case: If true, methods for Java objects that are passed across the bridge
            will have their names converted from camel case to underscores. i.e. class.methodName()
            becomes class.method_name()
        :type convert_camel_case: boolean
        :param debug: print helpful stuff for debugging
        :type debug: bool
        """
        self._context = zmq.Context()
        self._convert_camel_case = convert_camel_case
        self._debug = debug
        self._master_socket = JavaSocket(self._context, port, zmq.REQ, debug=debug)
        self._master_socket.send({'command': 'connect', })
        self._class_factory = JavaClassFactory()
        reply_json = self._master_socket.receive(timeout=500)
        if reply_json is None:
            raise TimeoutError("Socket timed out after 500 milliseconds. Is Micro-Manager running and is the ZMQ server option enabled?")
        if reply_json['type'] == 'exception':
            raise Exception(reply_json['message'])
        if 'version' not in reply_json:
            reply_json['version'] = '2.0.0' #before version was added
        if reply_json['version'] != self._EXPECTED_ZMQ_SERVER_VERSION:
            warnings.warn('Version mistmatch between Java ZMQ server and Python client. '
                            '\nJava ZMQ server version: {}\nPython client expected version: {}'.format(reply_json['version'],
                                                                                           self._EXPECTED_ZMQ_SERVER_VERSION))

    def get_class(self, serialized_object) -> typing.Type[JavaObjectShadow]:
        return self._class_factory.create(serialized_object, convert_camel_case=self._convert_camel_case)

    def construct_java_object(self, classpath, new_socket=False, args=None):
        """
        Create a new instance of a an object on the Java side. Returns a Python "Shadow" of the object, which behaves
        just like the object on the Java side (i.e. same methods, fields). Methods of the object can be inferred at
        runtime using iPython autocomplete

        :param classpath: Full classpath of the java object
        :type classpath: string
        :param new_socket: If true, will create new java object on a new port so that blocking calls will not interfere
            with the bridges master port
        :param args: list of arguments to the constructor, if applicable
        :type args: list
        :return: Python  "Shadow" to the Java object
        """
        if args is None:
            args = []
        # classpath_minus_class = '.'.join(classpath.split('.')[:-1])
        #query the server for constructors matching this classpath
        message = {'command': 'get-constructors', 'classpath': classpath}
        self._master_socket.send(message)
        constructors = self._master_socket.receive()['api']

        methods_with_name = [m for m in constructors if m['name'] == classpath]
        if len(methods_with_name) == 0:
            raise Exception('No valid java constructor found with classpath {}'.format(classpath))
        valid_method_spec = _check_method_args(methods_with_name, args)

        # Calling a constructor, rather than getting return from method
        message = {'command': 'constructor', 'classpath': classpath,
                   'argument-types': valid_method_spec['arguments'],
                   'arguments': _package_arguments(valid_method_spec, args)}
        if new_socket:
            message['new-port'] = True
        self._master_socket.send(message)
        serialized_object = self._master_socket.receive()
        if new_socket:
            socket = JavaSocket(self._context, serialized_object['port'], zmq.REQ)
        else:
            socket = self._master_socket
        return self._class_factory.create(serialized_object)(socket=socket, serialized_object=serialized_object, bridge=self)

    def _connect_push(self, port):
        """
        Connect a push socket on the given port
        :param port:
        :return:
        """
        return JavaSocket(self._context, port, zmq.PUSH, debug=self._debug)

    def _connect_pull(self, port):
        """
        Connect to a pull socket on the given port
        :param port:
        :return:
        """
        return JavaSocket(self._context, port, zmq.PULL, debug=self._debug)


    def get_magellan(self):
        """
        return an instance of the Micro-Magellan API
        """
        return self.construct_java_object('org.micromanager.magellan.api.MagellanAPI')

    def get_core(self):
        """
        Connect to CMMCore and return object that has its methods

        :return: Python "shadow" object for micromanager core
        """
        if hasattr(self, 'core'):
            return getattr(self, 'core')
        return self.construct_java_object('mmcorej.CMMCore')

    def get_studio(self):
        """
        return an instance of the Studio object that provides access to micro-manager Java APIs
        """
        return self.construct_java_object('org.micromanager.Studio')


class JavaSocket:
    """
    Wrapper for ZMQ socket that sends and recieves dictionaries
    """

    def __init__(self, context, port, type, debug):
        # request reply socket
        self._socket = context.socket(type)
        self._debug = debug
        # try:
        if type == zmq.PUSH:
            if debug:
                print('binding {}'.format(port))
            self._socket.bind("tcp://127.0.0.1:{}".format(port))
        else:
            if debug:
                print('connecting {}'.format(port))
            self._socket.connect("tcp://127.0.0.1:{}".format(port))
        # except Exception as e:
        #     print(e.__traceback__)
        # raise Exception('Couldnt connect or bind to port {}'.format(port))

    def _convert_np_to_python(self, d):
        """
        recursive ply search dictionary and convert any values from numpy floats/ints to
        python floats/ints so they can be hson serialized
        :return:
        """
        if type(d) != dict:
            return
        for k, v in d.items():
            if isinstance(v, dict):
                self._convert_np_to_python(v)
            elif type(v) == list:
                for e in v:
                    self._convert_np_to_python(e)
            elif np.issubdtype(type(v), np.floating):
                d[k] = float(v)
            elif np.issubdtype(type(v), np.integer):
                d[k] = int(v)

    def send(self, message, timeout=0):
        if message is None:
            message = {}
        #make sure any np types convert to python types so they can be json serialized
        self._convert_np_to_python(message)
        if timeout == 0:
            self._socket.send(bytes(json.dumps(message), 'utf-8'))
        else:
            start = time.time()
            while 1000 * (time.time() - start) < timeout:
                try:
                    self._socket.send(bytes(json.dumps(message), 'utf-8'), flags=zmq.NOBLOCK)
                    return True
                except zmq.ZMQError:
                    pass #ignore, keep trying
            return False

    def receive(self, timeout=0):
        if timeout == 0:
            reply = self._socket.recv()
        else:
            start = time.time()
            reply = None
            while 1000 * (time.time() - start) < timeout:
                try:
                    reply = self._socket.recv(flags=zmq.NOBLOCK)
                    if reply is not None:
                        break
                except zmq.ZMQError:
                    pass #ignore, keep trying
            if reply is None:
                return reply
        message = json.loads(reply.decode('utf-8'))
        self._check_exception(message)
        return message

    def _check_exception(self, response):
        if ('type' in response and response['type'] == 'exception'):
            raise Exception(response['value'])

    def close(self):
        self._socket.close()