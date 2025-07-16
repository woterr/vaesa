import sys
import os
import threading
import time

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from peer.peer import Peer
from utils.ports import get_ports



def get_peer_creds():
    # read host and port from credentials.txt or prompt the user

    # This is based on user's local machine, hence nothing will be logged.

    HOST = ""
    PORT = 0
    ports = get_ports()

    try:
        with open("CREDENTIALS.txt", "r") as f:
            CREDS = f.read().strip().split(" ")
            if len(CREDS) == 2:
                HOST = CREDS[0]
                try:
                    PORT = int(CREDS[1])
                    for i in ports:
                        if i == PORT:
                            print(f"[ SYSTEM ]: Port {PORT} from CREDENTIALS.txt is already in use.")
                            PORT = int(input("[ SYSTEM ]: Please enter a different SENDER PORT: "))
                            while PORT in ports:
                                PORT = int(input(f"[ SYSTEM ]: Port {PORT} is still in use. Enter a different SENDER PORT: "))
                except ValueError:
                    raise IndexError
            else:
                raise IndexError
    except (FileNotFoundError, IndexError, ValueError):
        # handle cases where file is empty or non existent or partially filled
        print("[ SYSTEM ]: CREDENTIALS.txt not found or invalid. Prompting for details.")
        HOST = input("[ SYSTEM ]: Enter SENDER IP (e.g., 127.0.0.1): ")
        PORT = int(input("[ SYSTEM ]: Enter SENDER PORT: "))
        # Keep prompting until a free port is entered
        while PORT in ports:
            PORT = int(input(f"[ SYSTEM ]: Port {PORT} is already in use. Enter a different SENDER PORT: "))
        
    try:
        with open("CREDENTIALS.txt", "w") as f:
            f.write(f"{HOST} {PORT}")
        print(f"[ SYSTEM ]: Credentials saved to CREDENTIALS.txt: {HOST}:{PORT}")

    except IOError:
        print("[ SYSTEM ]: Warning: Could not save credentials to CREDENTIALS.txt.")

    return HOST, PORT


def dislpay_ui():
    print("\n--- Peer-to-Peer Chat Menu ---")
    print("1. Initialize connection to another peer")
    print("2. Wait for connection from another peer")
    print("3. Send messages (enter message mode)")
    print("4. Exit")
    print("------------------------------")

    choice = input("[ MENU ]: Enter your choice (1-4): ").strip()
    return choice

def send_messages(peer):
    # send messages until the peer types _menu_

    print("[ MESSAGE MODE ] Type your messages. Type '_menu_' to return to the main menu")
    while True:
        try:
            msg = input("[ YOU ]: ")
            if msg.lower() == '_menu_':
                print("[ MESSAGE MODE ]: Returning to main menu.")
                break
            peer.send_data(msg)

        except (KeyboardInterrupt, EOFError):

            print("[ MESSAGE MODE ]: Exiting message mode due to interrupt.")
            break

        except Exception as e:
            print(f"[ MESSAGE MODE ERROR ]: An error occurred while sending the message: {e}")
            break

def main():
    HOST, PORT = get_peer_creds()

    peer = Peer(HOST, PORT)
    print(f"[ SYSTEM ]: Starting peer listener on {HOST}:{PORT}...")
    threading.Thread(target=peer.start_peer, daemon=True).start()
    time.sleep(1)

    try:
        while True:
            choice = dislpay_ui()

            if choice == '1': # init connection to another peer
                print("[ SYSTEM ]: Initializing connection to another peer...")
                recv_host = input("[ SYSTEM ]: Enter RECEIVER IP: ")
                recv_port = int(input("[ SYSTEM ]: Enter RECEIVER PORT: "))
                peer.connect_req(peer_host=recv_host, peer_port=recv_port)
                
                send_messages(peer)
            elif choice == '2': # get connection from another peer
                print(f"[ SYSTEM ]: Peer is listening on {peer.host}:{peer.port}.")
                print("[ SYSTEM ]: Waiting for an incoming connection from another peer...")
                print("[ SYSTEM ]: You can enter message mode now, but messages will only be sent once you are connected.")

                send_messages(peer)
            elif choice == '3': # enter msg mode
                send_messages(peer)
            elif choice == '4': # exit
                print("[ SYSTEM ]: Exiting application. Goodbye!")
                break
            else:
                print("[ SYSTEM ]: Invalid choice. Please enter a number between 1 and 4.")
            
            time.sleep(.1)
    except (KeyboardInterrupt, EOFError):
        print("\n[ SYSTEM ]: Application interrupted. Exiting gracefully.")
    except Exception as e:
        print(f"[ ERROR ]: An unexpected error occurred: {e}")

    
if __name__ == "__main__":
    main()