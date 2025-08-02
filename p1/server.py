# Process 1 - Server

from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread
from node import Node 
from config import PROCESS_ID, PEERS

def start_server(port):
    server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
    print(f"[RPC Server {PROCESS_ID}] Started on port {port}")

    # Create node instance
    node_instance = Node(PROCESS_ID, PEERS)

    # Register Lamport RPC functions from the node instance
    server.register_function(node_instance.receive_request)
    server.register_function(node_instance.receive_reply)
    server.register_function(node_instance.receive_release)

    # Optional: expose other methods too
    # server.register_function(node_instance.request_critical_section)

    # Run in a background thread
    thread = Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    return node_instance
