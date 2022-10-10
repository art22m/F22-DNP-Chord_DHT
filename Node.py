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
import threading
from concurrent import futures

# Config

REGISTRY_HOST = '127.0.0.1'
REGISTRY_PORT = '5555'

HOST = '127.0.0.1'
PORT = '5001'

FETCH_FINGER_TABLE_TIME_INTERVAL = 30.0
SEED = 0
MAX_WORKERS = 10

registry_channel = None
registry_stub = None

# Variables

node_id = None
key_size = 4
predecessor_id = None
finger_table = {}


# Helper

def terminate(message):
    log(message)
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


class NodeHandler(pb2_grpc.NodeServiceServicer):

    def get_finger_table(self, request, context):

        raise NotImplementedError('Method not implemented!')


def fetch_finger_table():
    message = pb2.PopulateFingerTableRequest(node_id=node_id)
    populate_finger_table_response = registry_stub.populate_finger_table(message)

    finger_table_message = populate_finger_table_response.finger_table
    new_finger_table = {}

    # FIXME: Возможно будут проблемы с многопоточкой (мьютекс нунжен)
    for row in finger_table_message:
        new_finger_table[row.id] = row.socket_addr

    global predecessor_id
    predecessor_id = populate_finger_table_response.node_id

    global finger_table
    finger_table = new_finger_table

    log(finger_table)


def start_fetching_finger_table():
    threading.Timer(FETCH_FINGER_TABLE_TIME_INTERVAL, start_fetching_finger_table).start()
    fetch_finger_table()


def connect_to_registry():
    global registry_channel
    registry_channel = grpc.insecure_channel(f"{REGISTRY_HOST}:{REGISTRY_PORT}")

    global registry_stub
    registry_stub = pb2_grpc.RegistryServiceStub(registry_channel)


def register_in_chord():
    message = pb2.RegisterRequest(ipaddr=HOST, port=PORT)
    registry_response = registry_stub.register(message)

    # Fail
    if registry_response.node_id == '-1':
        terminate(f"Cannot register node: {registry_response.message}")

    # Success
    global node_id
    node_id = int(registry_response.node_id)

    global key_size
    key_size = int(registry_response.message)


def start_node():
    # Connect to registry
    connect_to_registry()

    # Try to register self in the chord
    register_in_chord()

    # Start thread to get finger_table every 1 second
    start_fetching_finger_table()

    # while 1:
    #     q = 1


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    start_node()
