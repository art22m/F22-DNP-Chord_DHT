"""
--------
Registry
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

HOST = '127.0.0.1'
PORT = '5555'

KEY_SIZE = 4

SEED = 0
MAX_WORKERS = 10

random.seed(SEED)


# Variables

node_dict = {}


# Helper functions

def terminate(message):
    log(message)
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


def get_error_message(error):
    if error == 'invalid arg':
        return 'Please, run the registry again with argument <port> <size of key>\n example: python3 Registry.py 5000 5'
    elif error == 'invalid port':
        return 'Invalid format of the port, integer in the range [1, 65535] is expected'
    elif error == 'invalid key size':
        return 'Invalid format of the key size, integer is expected'
    else:
        return 'Invalid input'


def parse_arg(args):
    if len(args) != 3:
        terminate(get_error_message('invalid arg'))

    # Port checking
    try:
        port = int(args[1])
    except:
        terminate(get_error_message('invalid port'))

    if port > 65535 or port < 1:
        terminate(get_error_message('invalid port'))

    # Key checking
    try:
        key_size = int(args[2])
    except:
        terminate(get_error_message('invalid key size'))

    global PORT
    global KEY_SIZE

    PORT = port
    KEY_SIZE = key_size


# Registry Handler

class RegistryHandler(pb2_grpc.InnoServiceServicer):

    def register(self, request, context):
        ipaddr = request.ipaddr
        port = request.port

        try:
            new_id = generate_node_id()
            message = KEY_SIZE

            node_dict[new_id] = (ipaddr, port)

        except Exception as error_message:
            new_id = -1
            message = str(error_message)

        return pb2.RegisterReply(id=new_id, message=message)


    def deregister(self, request, context):
        node_id = request.id

        try:
            node_dict.pop(node_id)
            message = f"Node with id {node_id} successfully deleted."
            result = True

        except:
            message = f"Node with id {node_id} is not exist."
            result = False

        return pb2.DeregisterReply(result=result, message=message)


    def populateFingerTable(self, request, context):
        node_id = request.id

        finger_table = get_finger_table(node_id)
        finger_table_message = []

        # TODO: Refactor
        for row in finger_table:
            # row[0] - successor id, row[1] - (ip_address, port)
            finger_table_message.append(pb2.Node(id=row[0], ipaddr=f"{row[1][0]}:{row[1][1]}"))

        predecessor_id = get_predecessor_id(node_id)
        return pb2.DeregisterReply(id=predecessor_id, fingerTable=finger_table_message)


    def getChordInfo(self, request, context):
        raise NotImplementedError('Method not implemented!')


# Other Functions

def generate_node_id() -> int:
    if len(node_dict) == KEY_SIZE:
        raise Exception("Chord is full")

    while True:
        new_id = random.randint(0, KEY_SIZE)
        if node_dict.get(new_id) is None:
            return new_id


def get_finger_table(node_id):
    finger_table = []

    for i in range(0, KEY_SIZE):
        pos = (node_id + 2 ** i) % (2 ** KEY_SIZE)
        successor_id = get_successor_id(pos)
        finger_table.append((successor_id, node_dict[successor_id]))

    return finger_table


def get_successor_id(node_id) -> int:
    all_id = node_dict.keys()

    min_delta = 2 ** KEY_SIZE
    successor_id = -1
    min_id = 2 ** KEY_SIZE

    print(all_id)

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


def get_predecessor_id(node_id) -> int:
    all_id = node_dict.keys()

    min_delta = 2 ** KEY_SIZE
    predecessor_id = -1
    max_id = 0

    # Find the closest id to the given one and having the smaller value
    for current_id in all_id:
        delta = current_id - node_id
        max_id = max(max_id, current_id)
        if delta < 0 and min_delta > abs(delta):
            min_delta = abs(delta)
            predecessor_id = current_id

    # If no predecessor found, set it to the largest id in the chord
    if predecessor_id == -1:
        predecessor_id = max_id

    return predecessor_id


# Init

def start_registry():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    pb2_grpc.add_InnoServiceServicer_to_server(RegistryHandler(), server)
    server.add_insecure_port(f"{HOST}:{PORT}")
    server.start()

    try:
        server.wait_for_termination()

    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    # TODO: uncomment
    # parse_arg(sys.argv)

    # start_registry()
