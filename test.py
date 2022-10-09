
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


node_dict[32] = 1
node_dict[40] = 1
node_dict[45] = 1
node_dict[99] = 1
# node_dict[132] = 1
# node_dict[198] = 1
# node_dict[234] = 1

new_id = get_predecessor_id(31)

print(new_id)