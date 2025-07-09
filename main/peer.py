import socket
import threading
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logs_config import comms_logger, net_logger, error_logger
from utils.ports import get_ports
from encryption.session_keys import decypt_sk, gen_sk, encrypt_sk
from encryption.rsa_keypair import public_bytes, private_bytes
from encryption.aes_encrypt import encrypt_data, decrypt_data

class Peer:
    # initialise port and host, and socket
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # make it possible to have more than a single connection
        self.connections = []
        self.addr_map = {}
        # security
        self.session_key = None

    # start listening on a port
    def start_peer(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        print(f'[ SYSTEM ] Lisitening on PORT {self.port}')
        net_logger.info(f'A PEER is listening on PORT {self.port}')
        threading.Thread(target=self.accept_req, daemon=True).start()
        
    # accept connections from other ports
    def accept_req(self):
        while True:
            conn, addr = self.socket.accept()
            self.connections.append(conn)
            self.addr_map[conn] = addr
            print(f"[ SYSTEM ] Connected to: {addr}")
            net_logger.info(f'{self.host}:{self.port} accepted connection from {addr}')

            # recieve public key
            length = int.from_bytes(conn.recv(4), 'big')
            public_bytes = conn.recv(length)
            print(f"[ SYSTEM ] Recieved public key from {addr}")
            net_logger.info(f'{self.host}:{self.port} Recieved public key from {addr}')

            # generate session key and encrypt with the public key u got
            
            self.session_key = gen_sk()
            print(f"[ SYSTEM ] Generated session key for {addr}")
            encrypted_sk = encrypt_sk(self.session_key, public_bytes)
            print(f"[ SYSTEM ] Encrypted session key for {addr}")

            # send the encrypted session key back to the peer
            conn.sendall(len(encrypted_sk).to_bytes(2, 'big') + encrypted_sk)
            print(f"[ SYSTEM ] Sent encrypted session key to {addr}")
            net_logger.info(f'{self.host}:{self.port} Sent encrypted session key to {addr}')

            threading.Thread(target=self.receive_data, args=(conn,), daemon=True).start()

    # send requestion to other ports
    def connect_req(self, peer_host, peer_port):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((peer_host, peer_port))

        # add connection to array of connections
        self.connections.append(conn)
        self.addr_map[conn] = (peer_host, peer_port)

        print(f"[ PEER ] Connected to {peer_host}:{peer_port}")
        net_logger.info(f'{self.host}:{self.port} connected to {peer_host}:{peer_port}')

        # send public key
        conn.sendall(len(public_bytes).to_bytes(4, 'big') + public_bytes)
        print(f"[ PEER ] Sent public key to {peer_host}:{peer_port}")
        net_logger.info(f'{self.host}:{self.port} sent its public key to {peer_host}:{peer_port}')


        # get the encrypted session key (encrypted using public key) to decrypt using my private key
        length = int.from_bytes(conn.recv(2), 'big')
        encrypted_sk = conn.recv(length)

        self.session_key = decypt_sk(encrypted_sk, private_bytes)
        print(f"[ PEER ] Recieved session key from {peer_host}:{peer_port}")
        net_logger.info(f'{self.host}:{self.port} recieved session key from {peer_host}:{peer_port} - {self.session_key.hex()}')
        threading.Thread(target=self.receive_data, args=(conn,), daemon=True).start()


    # get data from other ports after connection
    def receive_data(self, conn):
        while True:
            try:
                # wait for bytes
                sender = self.addr_map.get(conn, ('Unknown', 0))
                received_data = conn.recv(4096).decode()
                fields = dict(field.split("::") for field in received_data.split("||"))
                iv = bytes.fromhex(fields['iv'])
                encrytped_data = bytes.fromhex(fields['data'])

                data = decrypt_data(self.session_key, iv, encrytped_data)

                if not data:
                    print(f"[ SYSTEM ] Connection closed by PEER {sender[0]}:{sender[1]}")
                    net_logger.info(f'{self.host}:{self.port} Closed connection with {sender[0]}:{sender[1]}')
                    break

                print(f"\n[ RECEIVED from {sender[0]}:{sender[1]} ]: {data}")
                comms_logger.info(f'{self.host}:{self.port} received: {encrytped_data.hex()} from {sender[0]}:{sender[1]}') 
                print("[ MESSAGE (YOU) ]: ", end='', flush=True)
 
            # incase connection dies out
            except ConnectionResetError:
                print("[ ERROR ] Connection reset by PEER")
                net_logger.info(f'{self.host}:{self.port} Reset connection')
                break
            except Exception as e:
                print(f"[ ERROR ]: {e}")
                error_logger.error(f'{self.host}:{self.port} - {e}')
                break

    def send_data(self, message):
        # send data to all connections
        for conn in self.connections:
            try:
                if self.session_key:

                    iv, cipher = encrypt_data(self.session_key, message.encode())
                    msg = f"iv::{iv.hex()}||data::{cipher.hex()}".encode()
                    conn.sendall(msg)

                    comms_logger.info(f'{self.host}:{self.port} Sent: {cipher.hex()}')
                else:
                    print("Session key does not exist.")
            except Exception as e:
                error_logger.error(f"{self.host}:{self.port} Failed to send message: {e}")
                continue


if __name__ == "__main__":
    import time
    ports = get_ports()
    
    with open("CREDENTIALS.txt", "r") as f:
        CREDS = f.read().split(" ")
        try:
            HOST, PORT = CREDS[0], int(CREDS[1])
            for i in ports:
                if i == PORT:
                    PORT = int(input("[ SYSTEM ]: This PORT is already being used. Enter SENDER PORT: "))
        except IndexError:
            HOST = input("[ SYSTEM ]: Enter SENDER IP: ")
            PORT = int(input("[ SYSTEM ]: Enter SENDER PORT: "))
            for i in ports:
                if i == PORT:
                    PORT = int(input("[ SYSTEM ]: This PORT is already being used. Enter SENDER PORT: "))


    peer = Peer(HOST, PORT) # create object
    peer.start_peer()

    accepting_param = ["y", "1", "yes"]
    conn_bool = input("Connect to another peer? y/n: ").strip().lower() in accepting_param

    def user_input_loop(peer):
        while True:
            try:
                msg = input("[ MESSAGE (YOU) ]: ")
                peer.send_data(msg)
            except (KeyboardInterrupt, EOFError):
                break

    # FIX THIS TO MAKE THE UI EXPERIENCE BETTER
    if conn_bool:
        initiator_bool = input("Are you the initiator? (Yes if initiator, else wait for connection): ").strip().lower() in accepting_param

        if initiator_bool:
            for i in ports:
                if i != PORT:
                    print(f'RECIEVER PORT on this host: {i}')
            recv_host = (input("Enter RECIEVER IP: "))
            recv_port = int(input("Enter RECIEVER PORT: "))
            peer.connect_req(peer_host=recv_host, peer_port=recv_port)
        else:
            pass

        threading.Thread(target=user_input_loop, args=(peer,), daemon=True).start()

        while True:
            time.sleep(0.1)