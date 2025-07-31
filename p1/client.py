# Process 1 - Client

import xmlrpc.client
from config import PEERS
from config import PROCESS_ID

def send_request_to_all(timestamp, process_id):
    for peer_name, url in PEERS.items():
        try:
            proxy = xmlrpc.client.ServerProxy(url)
            proxy.receive_request(timestamp, process_id)
            print(f"[RPC Client: {PROCESS_ID}] Sent request to {peer_name}")
        except Exception as e:
            print(f"[RPC Client: {PROCESS_ID}] Failed to send request to {peer_name}: {e}")

def send_reply(to_url, process_id):
    try:
        proxy = xmlrpc.client.ServerProxy(to_url)
        proxy.receive_reply(process_id)
        print(f"[RPC Client: {PROCESS_ID}] Sent reply to {to_url}")
    except Exception as e:
        print(f"[RPC Client: {PROCESS_ID}] Failed to send reply: {e}")

def send_release_to_all(process_id):
    for peer_name, url in PEERS.items():
        try:
            proxy = xmlrpc.client.ServerProxy(url)
            proxy.receive_release(process_id)
            print(f"[RPC Client: {PROCESS_ID}] Sent release to {peer_name}")
        except Exception as e:
            print(f"[RPC Client: {PROCESS_ID}] Failed to send release to {peer_name}: {e}")
