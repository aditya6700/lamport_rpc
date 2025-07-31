# Process 2 - Server

from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread
import node
from config import PROCESS_ID

def start_server(port):
    server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
    print(f"[RPC Server {PROCESS_ID}] Started on port {port}")

    # Register Lamport RPC functions
    server.register_function(node.receive_request)
    server.register_function(node.receive_reply)
    server.register_function(node.receive_release)

    # Run in a background thread
    thread = Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
