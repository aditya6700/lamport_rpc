# Process 3 - Main

import time
from server import start_server
from node import Node
from config import PROCESS_ID, PEERS, PORT

# node = Node(PROCESS_ID, PEERS)

def run():
    node = start_server(PORT)
    time.sleep(1)  # Let the server start

    # Only one process should request CS
    user_input = input(f"Do you want Node {PROCESS_ID} to enter Critical Section? (y/n): ")
    if user_input.strip().lower() == 'y':
        node.request_critical_section()

    # Keep main alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    run()
