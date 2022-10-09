"""
--------
Registry
--------

DNP Lab 5: Chord
Students: Vagif Khalilov, Artem Murashko
Emails: v.khalilov@innopolis.university, ar.murashko@innopolis.univeristy
Group: BS20-SD-01
"""

import sys
import signal

# Config

HOST = '127.0.0.1'
PORT = '5555'
KEY_SIZE = 4


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


# Console argument parse

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

# def register(ipaddr, port):
# def deregister(id):
# def populate_finger_table(id):
# def get_chord_info():
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    # TODO: uncomment
    # parse_arg(sys.argv)

