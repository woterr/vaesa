import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import threading
from peer.peer import Peer
from utils.ports import get_ports

def main():

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

    # FIX THIS TO MAKE THE UX BETTER
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

if __name__ == "__main__":
    main()