"""
--------
Client
--------

DNP Lab 5: Chord
Students: Vagif Khalilov, Artem Murashko
Emails: v.khalilov@innopolis.university, ar.murashko@innopolis.univeristy
Group: BS20-SD-01
"""

# Imports

import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc

import grpc
import sys
import signal
import time
import threading

from concurrent import futures
from threading import Thread

# Config

SERVER_CONNECTION_TIMEOUT = 1.5
SERVER_RESPONSE_TIMEOUT = 0.2

registry_channel = None
registry_stub = None

node_channel = None
node_stub = None

# Helper

def terminate(message):
    log(message)
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


# Client Functions

def close_current_connection():
    global registry_channel
    global registry_stub

    global node_channel
    global node_stub

    if registry_channel is not None:
        registry_channel.close()
    elif node_channel is not None:
        node_channel.close()

    registry_channel = None
    registry_stub = None
    node_channel = None
    node_stub = None

def connect(ipaddr, port):
    # FIXME: Нужна не костыльная проверка, подключились ли с правильным стабом.

    close_current_connection()

    # Try to connect to registry

    global registry_channel
    global registry_stub

    registry_channel = grpc.insecure_channel(f"{ipaddr}:{port}")
    try:
        grpc.channel_ready_future(registry_channel).result(timeout=SERVER_CONNECTION_TIMEOUT)
        registry_stub = pb2_grpc.RegistryServiceStub(registry_channel)

        message = pb2.GetChordInfoRequest()
        registry_stub.get_chord_info(message)
    except:
        registry_channel = None
        registry_stub = None
        pass
    else:
        log(f'Successfully connected to Registry with address {ipaddr}:{port}')
        return

    # Try to connect to node

    global node_channel
    global node_stub

    node_channel = grpc.insecure_channel(f"{ipaddr}:{port}")
    try:
        grpc.channel_ready_future(node_channel).result(timeout=SERVER_CONNECTION_TIMEOUT)
        node_stub = pb2_grpc.NodeServiceStub(node_channel)

        message = pb2.GetFingerTableRequest()
        node_stub.get_finger_table(message)
    except:
        node_channel = None
        node_stub = None
        pass
    else:
        log(f'Successfully connected to Node with address {ipaddr}:{port}')
        return

    log(f'There is no registry/node on {ipaddr}:{port}')


def get_info():
    if node_stub is not None:
        message = pb2.GetFingerTableRequest()
        try:
            get_finger_table_response = node_stub.get_finger_table(message, timeout=SERVER_RESPONSE_TIMEOUT)
        except grpc.RpcError:
            log("Node response timeout exceeded. Please, connect again.")
            close_current_connection()
            return

        log(f'Node id: {get_finger_table_response.node_id}')
        log('Finger table:')
        for node in get_finger_table_response.finger_table:
            log(f'{node.id}: {node.socket_addr}')

    elif registry_stub is not None:
        message = pb2.GetChordInfoRequest()
        try:
            get_chord_info_response = registry_stub.get_chord_info(message, timeout=SERVER_RESPONSE_TIMEOUT)
        except grpc.RpcError:
            log("Registry response timeout exceeded. Please, connect again.")
            close_current_connection()
            return

        for node in get_chord_info_response.nodes:
            log(f"{node.id} : {node.socket_addr}")

    else:
        log("You are not connected to the server.")
        log("Try connect <ipaddr>:<port> command")

def save(key, text):
    raise NotImplementedError('Method not implemented!')


def remove(key):
    raise NotImplementedError('Method not implemented!')


def find(key):
    raise NotImplementedError('Method not implemented!')


# Init

def print_help():
    log("Unknown command.")
    log(
        "Available commands: \n "
        "(1) connect <ipaddr>:<port>\n "
        "(2) get_info\n "
        "(3) save 'key' <text>\n "
        "(4) remove key\n "
        "(5) find key\n "
        "(6) quit"
        )
    log("")  # blank space


def start_client():
    while True:
        client_input = input('> ')

        command = client_input.split(' ', 1)[0]
        arguments = client_input.split(' ', 2)[1::]

        # connect
        if command == 'connect':
            ipaddr = arguments[0].split(':')[0]
            port = arguments[0].split(':')[1]
            connect(ipaddr, port)

        # get info
        elif command == 'get_info':
            get_info()

        # save “key” <text>
        elif command == 'save':
            key = arguments[0]
            text = arguments[1]
            save(key, text)

        # remove key
        elif command == 'remove':
            key = arguments[0]
            remove(key)

        # find key
        elif command == 'find':
            key = arguments[0]
            find(key)

        # quit
        elif command == 'quit':
            terminate("Terminating the client")

        else:
            print_help()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    try:
        start_client()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')
