import threading

KEY_SIZE = 8
node_dict = {}


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


# node_dict[32] = 1
# node_dict[40] = 1
# node_dict[45] = 1
# node_dict[99] = 1
# node_dict[132] = 1
# node_dict[198] = 1
# node_dict[234] = 1

# new_id = get_predecessor_id(31)
#
# print(new_id)
#
# socket_addr = ('123.123.2', 1233)
# ipaddr, port = socket_addr
#
# print(ipaddr)
# print(port)

msg = 'save 123 123 123 123 123123233 23'
print(msg.split(' ', 2))

mydict = {}
mydict[2] = {'123', '23'}
mydict[10] = {'12ads3', '23'}
mydict[24] = {'9912', '23'}
mydict[30] = {'23', '23'}

dict_list = list(mydict.items())
dict_list.sort()
mapped_dict_list = list(map(lambda x: [x[0] + 2 ** 5, x[1]], dict_list))
dict_list += mapped_dict_list
print(-1 % 32)
