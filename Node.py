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
import time
import threading

from concurrent import futures
from threading import Thread

# Config

REGISTRY_HOST = '127.0.0.1'
REGISTRY_PORT = '5555'

HOST = '127.0.0.1'
PORT = '5001'

FETCH_FINGER_TABLE_TIME_INTERVAL = 10.0
REGISTRY_CONNECTION_TIMEOUT = 3.0
REGISTRY_RESPONSE_TIMEOUT = 0.5

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

def terminate(message, closure=None):
    log(message)
    if closure is not None:
        closure()
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


class NodeHandler(pb2_grpc.NodeServiceServicer):

    def get_finger_table(self, request, context):
        finger_table_message = []
        for successor_id, socket_addr in finger_table.items():
            ipaddr, port = socket_addr
            finger_table_message.append(pb2.Node(id=successor_id, socket_addr=f"{ipaddr}:{port}"))

        return pb2.GetFingerTableReply(node_id=node_id, finger_table=finger_table_message)


def fetch_finger_table():
    message = pb2.PopulateFingerTableRequest(node_id=node_id)
    try:
        populate_finger_table_response = registry_stub.populate_finger_table(message, timeout=REGISTRY_RESPONSE_TIMEOUT)
    except grpc.RpcError:
        terminate("Registry response timeout exceeded. Close the connection.")

    finger_table_message = populate_finger_table_response.finger_table
    new_finger_table = {}

    # FIXME: Возможно будут проблемы с многопоточкой (мьютекс нунжен)
    for row in finger_table_message:
        ipaddr = row.socket_addr.split(':')[0]
        port = row.socket_addr.split(':')[1]
        new_finger_table[row.id] = (ipaddr, port)

    global predecessor_id
    predecessor_id = populate_finger_table_response.node_id

    global finger_table
    finger_table = new_finger_table

    log(f"Predecessor: {predecessor_id}")
    log(f"Finger table: {finger_table}")


def start_fetching_finger_table():
    while True:
        fetch_finger_table()
        time.sleep(FETCH_FINGER_TABLE_TIME_INTERVAL)


def register_in_chord():
    message = pb2.RegisterRequest(ipaddr=HOST, port=PORT)
    try:
        registry_response = registry_stub.register(message, timeout=REGISTRY_RESPONSE_TIMEOUT)
    except grpc.RpcError:
        terminate("Registry response timeout exceeded. Close the connection.")

    # Fail
    if registry_response.node_id == '-1':
        terminate(f"Cannot register node: {registry_response.message}")

    # Success
    global node_id
    node_id = int(registry_response.node_id)

    global key_size
    key_size = int(registry_response.message)


def deregister_in_chord():
    if node_id is None:
        terminate("Node is not registered yet")

    message = pb2.DeregisterRequest(node_id=node_id)
    try:
        registry_response = registry_stub.deregister(message, timeout=REGISTRY_RESPONSE_TIMEOUT)
    except grpc.RpcError:
        terminate("Registry response timeout exceeded. Close the connection.")

    # TODO: Add logic of deregister

    registry_channel.close()
    if registry_response.result:  # success
        terminate(registry_response.message)
    else:  # error
        terminate(registry_response.message)


def connect_to_registry():
    global registry_channel
    global registry_stub

    registry_channel = grpc.insecure_channel(f"{REGISTRY_HOST}:{REGISTRY_PORT}")
    try:
        grpc.channel_ready_future(registry_channel).result(timeout=REGISTRY_CONNECTION_TIMEOUT)
    except grpc.FutureTimeoutError:
        terminate("Cannot connect to the registry")
    else:
        registry_stub = pb2_grpc.RegistryServiceStub(registry_channel)


def start_node_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    pb2_grpc.add_NodeServiceServicer_to_server(NodeHandler(), server)
    server.add_insecure_port(f"{HOST}:{PORT}")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server', deregister_in_chord)


# Init


def start_node():
    # Connect to registry
    connect_to_registry()

    # Try to register self in the chord
    register_in_chord()

    # Start thread to get finger_table every 1 second
    fetcher_worker_thread = Thread(target=start_fetching_finger_table, args=(), daemon=True)
    fetcher_worker_thread.start()

    # Start Node server
    server_worker_thread = Thread(target=start_node_server, args=(), daemon=True)
    server_worker_thread.start()

    # Start console input handling
    while True:
        message = input('> ')

        if message == 'quit()':
            deregister_in_chord()
        else:
            log("Unknown command.")
            log("Available commands: \n (1) quit() - deregister node and terminate the program")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)
    PORT = sys.argv[1]
    print(PORT)
    try:
        start_node()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server', deregister_in_chord)
