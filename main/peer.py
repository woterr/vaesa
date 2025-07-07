import socket
import threading

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []

    def start_peer(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        print(f'[ PEER ] Lisitening on PORT {self.port}')
        threading.Thread(target=self.accept_req, daemon=True).start()

    def accept_req(self):
        while True:
            conn, addr = self.socket.accept()
            self.connections.append(conn)
            print(f"[ CONNECTED ] {addr}")
            threading.Thread(target=self.receive_data, args=(conn,), daemon=True).start()

    def connect_req(self, peer_host, peer_port):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((peer_host, peer_port))
        self.connections.append(conn)
        print(f"[ PEER ] Connected to {peer_host}:{peer_port}")
        threading.Thread(target=self.receive_data, args=(conn,), daemon=True).start()

    def receive_data(self, conn):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print("[ INFO ] Connection closed by peer.", flush=True)
                    break
                print(f"[ RECEIVED ]: {data.decode()}", flush=True)

            except ConnectionResetError:
                print("[ ERROR ] Connection reset by peer.")
                break
            except Exception as e:
                print(f"[ ERROR ]: {e}")
                break

    def send_data(self, message):
        for conn in self.connections:
            try:
                conn.sendall(message.encode())
            except:
                continue


if __name__ == "__main__":
    import time
    HOST = 'localhost'
    PORT = int(input("[ SYSTEM ]: Enter SENDER PORT:"))

    peer = Peer(HOST, PORT)
    peer.start_peer()

    conn_bool = input("Connect to another peer? y/n: ")
    conn_param = ["y", "1", ""]
    if conn_bool in conn_param:
        initiator_bool = input("Are you the initiator? (Yes if initiator, else wait for connection): ")
        if initiator_bool in conn_param:
            recv_port = int(input("Enter RECIEVER PORT: "))
            peer.connect_req(peer_host=HOST, peer_port=recv_port)

        while True:
            msg = input("\n[ MESSAGE (YOU) ]: ")
            peer.send_data(msg)
            time.sleep(0.1)
