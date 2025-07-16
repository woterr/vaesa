TODO

- Attacker:
  MITM, Spoofing
- Demo:
  Spoof, ECB Attacks, Padding Oracle attack
- Better UI

# Infrastructure

Data transfer stands as the most important aspect of the current world. The ability to share and receive new ideas and philosophies shaped the world that we currently live in. From a technological standpoint, communication is essentially the movement of packets over networks with the help of certain protocols.

This project is a secure peer-to-peer communication system over a custom network with simulated attacks. Inspired by military-grade communication architecture, it uses AES encryption and session key exchange.

## Understanding Peer-to-Peer networks

A Peer-to-Peer process deals with a netwrok structure where both the nodes act as both - a client, and a server. In contrast to P2P networks, a Server-Client network ensures that each node is acting as a client except a single node that acts as a server. This server node accepts incoming requests and returns data. It could return the data to the same client, or any other client connected to the network. 

Assume you're talking to a friend in secret. This is a Peer-to-Peer network. But suppose you have a group leader who sends messages from one person to another; this is a client-server network. 

## Project architecture

A PEER refers to a node in a Peer-to-Peer (P2P) communication system. Each peer can act both as a client and a server. When the system starts, it launches a server that listens on a specified port for incoming connections. Other peers in the network can establish connections to this port to initiate communication. Once connected, peers can both send and receive messages using the same socket interface. 

This implementation leverages Python’s built-in socket module to manage TCP connections. Each peer maintains a list of active connections and handles incoming data in real-time using multithreading to allow concurrent message exchange. These connections are uniquely identified using session IDs. All messages sent across the network pass through encrypted channels (AES-CBC), ensuring confidentiality.

### Threading

Threading allows multiple connections to a single PEER. Each connection can have its own thread, allowing it to receive data independently without blocking others. Without threading, the server would freeze while waiting for one peer to send data. This is mostly useful when a single PEER is broadcasting data to multiple PEERS (1,2,3) whereas the other PEERS have one-on-one communication with the main PEER.

![Multiple Connections](https://github.com/user-attachments/assets/e74c58e5-0c0e-4d07-8598-235b1bb2215c)

### Data Transmission

Data transmission between nodes is always done in bytes. Since the system uses TCP/IP to transfer data, we are reducing it to bytes before lending it off to the protocol. This is because the socket layer in Python (and in general networking) operates at the byte level. Strings and structured data must be encoded into bytes before being sent and decoded after being received. This design choice ensures compatibility with cryptographic operations and future support for more complex data types like files or JSON. 

![Message flow](https://github.com/user-attachments/assets/e4c8732d-8fde-42e5-a24c-e5bf5bed98c7)

### Logs

All data, activities, and errors within the system must be logged for future reference, and for further examination to find security breaches. When a PEER starts a server, the port and its host is logged to net.log. This allows us to see which peer is currently ready to communicate. Further, when a PEER disconnects, it is logged. If an error occurs during the setup, that is logged too. All messages sent from PEER to PEER are logged (encrypted). 

# Encryption and Security

All messages sent between peers are encrypted (and logged). The encryption workflow is described in the diagram:

![Encryption Flow](https://github.com/user-attachments/assets/9e480029-87c3-40d1-a08a-477bcf33655e)

This structure solves a good number of problems - as listed below:

- **Confidentiality**
	- Q: How do we ensure that only the intended recipient can read the message?
	- A: AES encrypts messages using a session key. These session keys have a unique session ID which allows multiple connections between different PEERS. Also, only the recipient who holds the correct session key (exchanged securely using RSA) can decrypt the message. **Eavesdroppers can't read the data**, even if they intercept it.
- **Key Distribution**
	- Q: How do we safely share encryption keys between two peers over an insecure channel?
	- A: The sender encrypts the AES session key with the receiver's public RSA key. Only the receiver can decrypt it using their private RSA key.
- **Forward Secrecy**
	- Q: What happens if a session key is compromised? Will past communication be exposed?
	- By generating a new session key for each connection, past messages remain secure if a key is leaked later. Compromise of one key ≠ compromise of all history.
- **Integrity and Tamper Protection**
	- Q: How do we know if someone tampered with the message in transit?
	- A: AES in CBC mode prevents meaningful tampering.
- **Scalability for Multi-Peer Networks**
	- Q: Scalability for Multi-Peer Networks
	- A: Each peer has its own session key per connection.
