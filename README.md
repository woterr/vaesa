TODO

- Attacker:
  MITM, Spoofing
- Demo:
  Spoof, ECB Attacks, Padding Oracle attack
- Encryption:
  RSA for session keys, and message encryption using AES



# Infrastructure

Data transfer stands as the most important aspect of the current world. The ability to share and receive new ideas and philosophies shaped the world that we currently live in. From a technological standpoint, communication is essentially the movement of packets over networks with the help of certain protocols.

This project is a secure peer-to-peer communication system over a custom network with simulated attacks. Inspired by military-grade communication architecture, it uses AES encryption and session key exchange. The project also demonstrates common cryptographic attack vectors and defense mechanisms. 

## Understanding Peer-to-Peer networks

A Peer-to-Peer process deals with a netwrok structure where both the nodes act as both - a client, and a server. In contrast to P2P networks, a Server-Client network ensures that each node is acting as a client except a single node that acts as a server. This server node accepts incoming requests and returns data. It could return the data to the same client, or any other client connected to the network. 

For example, assume you are talking to your friend in private. This is a P2P network. But assume you have a group leader who is conveying messages from one person to another, that is a client-server network. 

## Project architecture

A PEER refers to a node in a Peer-to-Peer (P2P) communication system. Each peer can act both as a client and a server. When the system starts, it launches a server that listens on a specified port for incoming connections. Other peers in the network can establish connections to this port to initiate communication. Once connected, peers can both send and receive messages using the same socket interface. 

This implementation leverages Python’s built-in socket module to manage TCP connections. Each peer maintains a list of active connections and handles incoming data in real-time using multithreading to allow concurrent message exchange. All messages sent across the network pass through encrypted channels (AES-CBC), ensuring confidentiality.

### Threading

Threading allows multiple connections to a single PEER. Each connection can have its own thread, allowing it to receive data independently without blocking others. Without threading, the server would freeze while waiting for one peer to send data. This is mostly useful when a single PEER is broadcasting data to multiple PEERS (1,2,3)whereas the other PEERS have one-on-one communication with the main PEER.

### Data Transmission

Data transmission between nodes is always done in bytes. Since the system uses TCP/IP to transfer data, we are reducing it to bytes before lending it off to the protocol. This is because the socket layer in Python (and in general networking) operates at the byte level. Strings and structured data must be encoded into bytes before being sent and decoded after being received. This design choice ensures compatibility with cryptographic operations and future support for more complex data types like files or JSON. 

### Logs

All data, activities, and errors within the system must be logged for future reference, and for further examination to find security breaches. When a PEER starts a server, the port and its host is logged to net.log. This allows us to see which peer is currently ready to communicate. Further, when a PEER disconnects, it is logged. If an error occurs during the setup, that is logged too. All messages sent from PEER to PEER are logged (encrypted). 

# Encryption and Security

