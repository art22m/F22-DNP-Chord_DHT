"""
--------
Node
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
import random

from concurrent import futures

# Config

REGISTRY_HOST = '127.0.0.1'
REGISTRY_PORT = '5555'

HOST = '127.0.0.1'
PORT = '5001'

SEED = 0
MAX_WORKERS = 10

registry_channel = None
registry_stub = None

# Variables

key_size = 4


# Helper

def terminate(message):
    log(message)
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


class NodeHandler(pb2_grpc.NodeServiceServicer):

    def get_finger_table(self, request, context):

        raise NotImplementedError('Method not implemented!')


def connect_to_registry():
    global registry_channel
    registry_channel = grpc.insecure_channel(f"{REGISTRY_HOST}:{REGISTRY_PORT}")

    global registry_stub
    registry_stub = pb2_grpc.RegistryServiceStub(registry_channel)


def register_in_chord():
    message = pb2.RegisterRequest(ipaddr=HOST, port=PORT)
    registry_response = registry_stub.register(message)

    print(registry_response.node_id)
    print(registry_response.message)


def start_node():
    # Connect to registry
    connect_to_registry()

    # Try to register self in the chord
    register_in_chord()

    # while 1:
    #     q = 1


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    start_node()
