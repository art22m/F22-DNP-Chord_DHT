# Chord
In computing, Chord is a protocol and algorithm for a peer-to-peer distributed hash table. A 
distributed hash table stores key-value pairs by assigning keys to different computers (known as 
"nodes"); a node will store the values for all the keys for which it is responsible. Chord 
specifies how keys are assigned to nodes, and how a node can discover the value for a given key 
by first locating the node responsible for that key.

## Registry

Registry is responsible for registering and deregistering the nodes.

### Registry features:

```
● It holds a dictionary of id and address port pairsof all registered nodes.
● Forms a finger-table for a specific node.
● Helps a node to join the ring.
● Every node knows about the registry.
● It is the only centralized part of the chord.
● There are no nodes in the ring at the start of the registry.
```
### Run command:

```
python3 Registry.py <port> <m>
```
Registry has several command-line arguments:
● _port_ - port number registry should run on.
● _m_ - size of key (in bits). Thus, max size of the chordring.

**Run command example:**
```
python3 Registry.py 5000 5
```

### Functions:
```
register(ipaddr, port) :
```
This method is invoked by a new node to register itself. It is responsible to register
the node with given ipaddr and port. I.e., assignsan id from identified space.
Id is chosen randomly from range [0, 2 m -1]. If thegenerated id already exists, it
generates another one until there is no collision.
Returns:
If successful: tuple of (node’s assigned id, m)
If unsuccessful: tuple of (-1, error message explaining why it was unsuccessful)
It fails when the Chord is full, i.e. there are already 2mnodes in the ring.


```
deregister(id):
```
This method is responsible for deregistering the node with the given id.
Returns:
If successful: tuple of (True, success message)
If unsuccessful: tuple of (False, error message)
It may fail, if there is no such registered id.

```
populate_finger_table(id):
```

This method is responsible for generating the dictionary of the pairs (id, ipaddr:port)
that the node with the given id can directly communicatewith.
Also, this method should find the predecessor of the node with the given id - the next
node reverse clockwise. For example, if there are no nodes between nodes with ids
31 and 2, then the predecessor of node 2 is node 31.
Returns:
Predecessor of the node with the given id , fingertable of the node with the given id
(list of pairs (id, ipaddr:port)).

```
get_chord_info()
```
This is the only method called by the client. This method returns the information
about the chord ring (all registered nodes): list of (node id, ipaddr:port).
Example:
(2, 127.0.0.1:5002)
(12, 127.0.0.1:5003)
(20, 127.0.0.1:5004)

### How to form a finger table:

Each node has a **finger table** containing _s ≤ m_ entries.
_m_ - key size in bits (passed as a command-line argument).

_FTp_ - finger table of node with id _p._

_FTp[i]_ - i-th entry in finger table of node p.

1. Calculate _FTp[i] = succ(p + 2i-1)_ where _i_ ∈ _[1, m]_
2. Remove duplicates.

## Node

A node of a chord ring.

### Node features:
● At the start, the node is not part of the chord.
● It first registers itself by calling the register function of the Registry.
● Calls the populate_finger_table function of the Registryevery second (only if it was
successfully registered in the ring).
● Calls the deregister function of the Registry on exit.
● Stores some keys (data) of the chord.
● Able to save and remove data.


### Run command:

```
python3 Node.py <registry-ipaddr>:<registry-port><ipaddr>:<port>
```
Command-line arguments:
● _<registry-ipaddr>:<registry-port>_ - ip address anda port number of the Registry.
● _<ipaddr>:<port>_ - ip address and a port number thisnode will be listening to.

### Functions:

```
get_finger_table()
```
This function is called by the client. It should just return the current finger table.

```
save(key, text):
```
Saves the key and the text on the corresponding node.
○ Calculates the hash of the given key and the id wherethe text should be
stored as follows:
import zlib
hash_value = zlib.adler32(key.encode())
target_id = hash_value % 2 ** m

○ Finds the corresponding node following the **lookupprocedure** (described
below).
_Returns:_
If successful: (True, Node id it was saved on). Notethat this id may differ from the
calculated one.
If unsuccessful: (False, Error message). For example, such a key may already exist.

```
remove(key)
```
Similar to the save method. But removes the key andthe text from the corresponding
node.
Returns
If successful: (True, Node id it was removed from)
If unsuccessful: (False, Error message)


```
find(key)
```
Find the node, the key and the textshould be savedon.
Returns:
If successful: (True, id, address:port) of the node this key is saved on.
If unsuccessful: (False, error message). For example, if the given key was never
saved.

```
quit()
```
This method is responsible for calling the deregister method of the Registry to quit
the chord and then shut down the Node.


It is called when the Node receives the KeyboardInterrupt signal.
Before shutting down:
○ It notifies its successor node (i.e., first node in its finger table) about the
change of predecessor. In other words, it replaces successor’s predecessor
with its own predecessor
○ It transfers all data in its storage to its successor
○ It notifies its predecessor node about the change of successor, i.e., it replaces
the predecessor's successor with its own successor.

### Lookup procedure:

Let’s suppose we asked node with id **p** to save key **k:**

● If k ∈ (pred(p), p] - current node ( p ) is the successorof a key k , thus k should be
stored on the current node.
○ Suppose node 31 is a predecessor of node 2 in chord with m=5. If the
calculated key k is 1, then this key should be savedin node 2
● Otherwise,to look up a key k , node with id p willforward the request to node with
index j from its finger table satisfying:
FTp[j] ≤ k < FTp[j + 1]
○ Suppose Node 24 with finger table FT 24 =[26, 31, 2,16] is asked to save the
key whose calculated id is 1. Then Node 24 selects the Node 31 since it is the
farthest node that doesn’t overstep calculated id (1).


## Client
Client is a command line user interface to interact with the chord ring.
It continuously listens to the user's input and has several commands.

### Run command:

```
python3 Client.py
```
### Commands:

```
connect <ipaddr>:<port>
```
Establish a connection with a node or a registry on a given address.
The client should be able to distinguish between a registry and a node.
If there is no registry/node on this address, print the corresponding message.
If the connection is successful, print the corresponding message

```
get_info
```
Calls get_chord_info() if connected to a registry.Or get_finger_table() if connected to a node. 
And prints the result.

```
save “key” <text>
```
Example:
_save “some key” some “text” here
key_ : some key
_text:_ some “text” here
Ittells the connected node to save the **text** withthe given **key**. Prints the result.

```
remove key
```
It tells the connected node to remove the text with the given **key**. Prints the result.

```
find key
```
Ittells the connected node to find a node with the **key**. Prints the result.

```
quit
```
Stop and exit client.


## Example:

1. Run Registry:
```
    python3 Registry.py 5555 5
```
2. Run 5 nodes:
```
    python3 Node.py 127.0.0.1:5555 127.0.0.1:
    python3 Node.py 127.0.0.1:5555 127.0.0.1:
    python3 Node.py 127.0.0.1:5555 127.0.0.1:
    python3 Node.py 127.0.0.1:5555 127.0.0.1:
    python3 Node.py 127.0.0.1:5555 127.0.0.1:
```
3. Run client:
```
    python3 Client.py
```

**Client output:**
```
> connect 127.0.0.1:
Connected to registry

> get_info
24: 127.0.0.1:
26: 127.0.0.1:
2: 127.0.0.1:
16: 127.0.0.1:
31: 127.0.0.1:

> connect 127.0.0.1:
Connected to node 24

> get_info
Node id: 24
Finger table:
26: 127.0.0.1:
31: 127.0.0.1:
2: 127.0.0.1:
16: 127.0.0.1:

> save “Kazan” This is text for Kazan
True, Kazan is saved in node 24

> save “Kazan” some other text
False, key Kazan already exists

> find Kazan


True, Kazan is saved in node 24
Address: 127.0.0.1:
> remove Kazan
True, Kazan removed from node 24

> find Kazan
False, key Kazan does not exist

>quit
Shutting down
```


