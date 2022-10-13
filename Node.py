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
import zlib
import threading

from concurrent import futures
from threading import Thread

# Config

REGISTRY_HOST = '127.0.0.1'
REGISTRY_PORT = '5555'

HOST = '127.0.0.1'
PORT = '5001'

FETCH_FINGER_TABLE_TIME_INTERVAL = 10.0
REGISTRY_CONNECTION_TIMEOUT = 1.5
REGISTRY_RESPONSE_TIMEOUT = 0.5
NODE_CONNECTION_TIMEOUT = 1.5
NODE_RESPONSE_TIMEOUT = 1

SEED = 0
MAX_WORKERS = 10

registry_channel = None
registry_stub = None

# Variables

node_id = None
key_size = 5
predecessor_id = None

finger_table = {}
node_dict = {}


# Helper

def terminate(message, closure=None):
    log(message)
    if closure is not None:
        closure()
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


class NodeHandler(pb2_grpc.NodeServiceServicer):
    next_node_channel = None
    next_node_stub = None

    def get_finger_table(self, request, context):
        finger_table_message = []
        for successor_id, socket_addr in finger_table.items():
            ipaddr, port = socket_addr
            finger_table_message.append(pb2.Node(id=successor_id, socket_addr=f"{ipaddr}:{port}"))

        return pb2.GetFingerTableReply(node_id=node_id, finger_table=finger_table_message)

    def save(self, request, context):
        key = request.key
        text = request.text
        hashed_key = hash_key(key)

        print(f'Save: {hashed_key}')

        if predecessor_id is None:
            fetch_finger_table()

        next_id = self._find_next_node_id(hashed_key)

        if next_id == -1:
            return pb2.SaveReply(result=False, message=f'Error message')
        elif next_id == node_id:
            if node_dict.get(hashed_key) is not None:
                return pb2.SaveReply(result=False, message=f'{key} is already exist in node {node_id}')

            node_dict[hashed_key] = text
            return pb2.SaveReply(result=True, message=f'{key} is saved in node {node_id}')

        return self._send_save_to_next_node(next_id, key, text)

    def _find_next_node_id(self, key):
        print(f"i am = {node_id}")
        print(f"predecessor = {predecessor_id}")
        if predecessor_id < key <= node_id or key <= node_id < predecessor_id or node_id < predecessor_id < key or node_id == key:
            print("I am in state 1")
            return node_id

        successor_id = get_current_node_successor_id()
        print(f"successor = {successor_id}")
        if node_id < key <= successor_id or successor_id < node_id < key or key <= successor_id < node_id or successor_id == key:
            print("I am in state 2")
            return successor_id

        next_id = - 1

        dict_list = list(finger_table.items())
        dict_list.sort()
        mapped_dict_list = list(map(lambda x: [x[0] + 2 ** key_size, x[1]], dict_list))
        dict_list += mapped_dict_list

        for i in range(0, len(dict_list) - 1):
            if dict_list[i][0] <= key < dict_list[i + 1][0] or dict_list[i][0] <= key + 2 ** key_size < dict_list[i + 1][0]:
                next_id = dict_list[i][0]
                break

        return -1 if next_id == -1 else next_id % 32

    def _connect_to_next_node(self, next_node_id):
        ipaddr, port = finger_table[next_node_id]

        self.next_node_channel = grpc.insecure_channel(f"{ipaddr}:{port}")
        try:
            grpc.channel_ready_future(self.next_node_channel).result(timeout=NODE_CONNECTION_TIMEOUT)
        except:
            self.next_node_channel = None
            self.next_node_stub = None
        else:
            self.next_node_stub = pb2_grpc.NodeServiceStub(self.next_node_channel)


    def _send_save_to_next_node(self, next_node_id, key, text):
        self._connect_to_next_node(next_node_id)

        if self.next_node_stub is None:
            return pb2.SaveReply(result=False, message=f'Unable to connect to node {next_node_id}')

        message = pb2.SaveRequest(key=key, text=text)
        try:
            get_save_key_response = self.next_node_stub.save(message, timeout=NODE_RESPONSE_TIMEOUT)
        except grpc.RpcError:
            self.next_node_channel = None
            self.next_node_stub = None
            return pb2.SaveReply(result=False, message=f'Node response timeout exceeded.  {next_node_id}')

        self.next_node_channel.close()
        self.next_node_channel = None
        self.next_node_stub = None

        return get_save_key_response


    #def remove(self, request, context):
    #    raise NotImplementedError()

    #def find(self, request, context):
    #    raise NotImplementedError()


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


def get_current_node_successor_id():
    all_id = finger_table.keys()

    min_delta = 2 ** key_size
    successor_id = -1
    min_id = 2 ** key_size

    # Find the closest id to the given one and having the greater value
    for current_id in all_id:
        delta = current_id - node_id
        min_id = min(min_id, current_id)
        if 0 < delta < min_delta:
            min_delta = delta
            successor_id = current_id

    # If no successor found, set it to the smallest id in the chord
    if successor_id == -1:
        successor_id = min_id

    return successor_id


def hash_key(key):
    hash_value = zlib.adler32(key.encode())
    target_id = hash_value % 2 ** key_size
    return target_id


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
        terminate("Cannot connect to the registry.")
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
        terminate(f'{keys} was pressed, terminating server.', deregister_in_chord)


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
            log("Available commands: \n (1) quit() - deregister node and terminate the program.")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)
    PORT = sys.argv[1]
    print(PORT)
    try:
        start_node()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server.', deregister_in_chord)
