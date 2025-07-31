# Process 1 - Node

from config import PROCESS_ID, PEERS
import client
import server
import time
import threading

lamport_clock = 0
request_queue = []
replies_received = set()
want_cs = False

def increment_clock(received_ts=None):
    global lamport_clock
    if received_ts is None:
        lamport_clock += 1
    else:
        lamport_clock = max(lamport_clock, received_ts) + 1

def receive_request(timestamp, from_id):
    increment_clock(timestamp)
    print(f"[{PROCESS_ID}] Received request from {from_id} with ts={timestamp}")
    request_queue.append((timestamp, from_id))
    request_queue.sort()
    return True

def receive_reply(from_id):
    replies_received.add(from_id)
    print(f"[{PROCESS_ID}] Received reply from {from_id}")
    return True

def receive_release(from_id):
    global request_queue
    request_queue = [r for r in request_queue if r[1] != from_id]
    print(f"[{PROCESS_ID}] {from_id} released CS")
    return True

def request_critical_section():
    global want_cs, replies_received
    increment_clock()
    want_cs = True
    replies_received = set()

    print(f"[{PROCESS_ID}] Requesting CS with ts={lamport_clock}")
    request_queue.append((lamport_clock, PROCESS_ID))
    client.send_request_to_all(lamport_clock, PROCESS_ID)

    # Wait until this node's request is at the front and all replies received
    while not is_okay_to_enter_cs():
        time.sleep(0.5)

    enter_critical_section()

def is_okay_to_enter_cs():
    return (
        request_queue[0][1] == PROCESS_ID
        and len(replies_received) == len(PEERS)
    )

def enter_critical_section():
    print(f"[{PROCESS_ID}] 🔒 Entering Critical Section")
    time.sleep(2)  # Simulate doing some work
    print(f"[{PROCESS_ID}] 🔓 Exiting Critical Section")
    release_critical_section()

def release_critical_section():
    global want_cs
    request_queue.pop(0)
    want_cs = False
    client.send_release_to_all(PROCESS_ID)
