import socket
import threading
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logs_config import comms_logger, net_logger, error_logger
from utils.ports import get_ports

stop_input = threading.Event()
class Peer:
    # initialise port and host, and socket
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # make it possible to have more than a single connection
        self.connections = []

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
            print(f"[ SYSTEM ] Connected to: {addr}")
            net_logger.info(f'{self.host}:{self.port} accepted connection from {addr}')
            stop_input.set()
            threading.Thread(target=self.receive_data, args=(conn,), daemon=True).start()

    # send requestion to other ports
    def connect_req(self, peer_host, peer_port):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((peer_host, peer_port))

        # add connection to array of connections
        self.connections.append(conn)

        print(f"[ PEER ] Connected to {peer_host}:{peer_port}")
        net_logger.info(f'{self.host}:{self.port} connected to {peer_host}:{peer_port}')
        threading.Thread(target=self.receive_data, args=(conn,), daemon=True).start()

    # get data from other ports after connection
    def receive_data(self, conn):
        while True:
            try:
                # wait for bytes
                data = conn.recv(1024)
                if not data:
                    print("[ SYSTEM ] Connection closed by PEER")
                    net_logger.info(f'{self.host}:{self.port} Closed connection')
                    break

                print(f"\n[ RECEIVED ]: {data.decode()}")
                comms_logger.info(f'{self.host}:{self.port} received: {data.decode()}') 
                print(" [ MESSAGE (YOU) ]: ", end='', flush=True)
 
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
                conn.sendall(message.encode()) # data transfer must happen through raw bites
                comms_logger.info(f'{self.host}:{self.port} Sent: {message}')
            except:
                continue


if __name__ == "__main__":
    import time
    ports = get_ports()
    with open("CREDENTIALS.txt", "r") as f:
        CREDS = f.read().split()
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

    conn_bool = input("Connect to another peer? y/n: ")
    accepting_param = ["y", "1", "", "yes"]

    # FIX THIS TO MAKE THE UI EXPERIENCE BETTER
    if conn_bool in accepting_param:
        initiator_bool = input("Are you the initiator? (Yes if initiator, else wait for connection): ")

        if initiator_bool in accepting_param:
            for i in ports:
                if i != PORT:
                    print(f'RECIEVER PORT on this host: {i}')
            recv_host = (input("Enter RECIEVER IP: "))
            recv_port = int(input("Enter RECIEVER PORT: "))
            peer.connect_req(peer_host=recv_host, peer_port=recv_port)

        while True:
            msg = input("\n[ MESSAGE (YOU) ]: ")
            peer.send_data(msg)
            time.sleep(0.1)
