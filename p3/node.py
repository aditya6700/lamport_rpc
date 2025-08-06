# Process 3 - Node

import time
import xmlrpc.client
import heapq

class Node:
    # class variables
    def __init__(self, pid, peers):
        self.pid = pid
        self.peers = peers
        self.lamport_clock = 0
        self.reply_count = 0
        self.pending_replies = set()
        self.in_critical_section = False
        self.request_queue = [] 
    
    # lamport clock Rule 1
    def increment_clock(self):
        self.lamport_clock += 1

    def receive_request(self, from_pid, timestamp):
        # lamport clock Rule 2
        self.lamport_clock = max(self.lamport_clock, timestamp) + 1
        request_tuple = (timestamp, from_pid)
        
        # Check for duplicate request and reply
        if self.in_critical_section or self.request_queue:
            if request_tuple not in self.request_queue:
                print(f"[RPC Client: {self.pid}] ---- Queuing REQUEST from Node {from_pid} (ts={timestamp})")
                heapq.heappush(self.request_queue, request_tuple)
            else:
                print(f"[RPC Client: {self.pid}] ---- Duplicate REQUEST from Node {from_pid} ignored.")
            return False
        else:
            print(f"[RPC Client: {self.pid}] ---- Replying immediately to Node {from_pid} (ts={timestamp})")
            self.increment_clock()
            return (True, self.lamport_clock)

    def receive_release(self, from_pid, timestamp):
        self.lamport_clock = max(self.lamport_clock, timestamp) + 1
        print(f"[RPC Client: {self.pid}] ---- Received RELEASE from Node {from_pid}")

        # Process next queued request (if any)
        if self.request_queue:
            next_ts, next_pid = heapq.heappop(self.request_queue)
            print(f"[RPC Client: {self.pid}] ---- Sending reply to queued Node {next_pid} (ts={next_ts})")
            self.increment_clock()  # Increment before sending reply
            self.send_reply_to_queued_request(next_pid, self.lamport_clock)

    def send_reply_to_queued_request(self, to_pid, reply_ts):
        if to_pid in self.peers:
            to_url = self.peers[to_pid]
            try:
                proxy = xmlrpc.client.ServerProxy(to_url)
                proxy.receive_reply(self.pid, reply_ts)  # Include timestamp
                print(f"[RPC Client: {self.pid}] ---- Sent reply to Node {to_pid} (ts={reply_ts})")
            except Exception as e:
                print(f"[RPC Client: {self.pid}] ---- Failed to send reply to Node {to_pid}: {e}")
                # Re-add to queue if failed
                heapq.heappush(self.request_queue, (reply_ts, to_pid))
    
    def request_critical_section(self):
        if self.in_critical_section:
            print(f"[RPC Client: {self.pid}] Already in CS, cannot request again.")
            return
    
        self.increment_clock()
        ts = self.lamport_clock
        self.reply_count = 0
        print(f"[RPC Client: {self.pid}] ---- Requesting CS with timestamp {ts}")
        
        self.pending_replies = set(self.peers.keys())

        # send request for every 30 seconds if response is not received
        while self.reply_count < len(self.peers):
            for peer in list(self.pending_replies):
                to_url = self.peers[peer]
                try:
                    self.send_request(to_url, peer, self.pid, ts)
                except Exception as e:
                    print(f"[RPC Client: {self.pid}] ---- Failed to contact {peer}: {e}")

            if self.reply_count < len(self.peers):
                print(f"[RPC Client: {self.pid}] ---- Waiting... Will retry after 30 seconds for: {self.pending_replies}")
                time.sleep(30)
    
    def send_request(self, to_url, to_peer, from_id, timestamp):
        try:
            proxy = xmlrpc.client.ServerProxy(to_url)
            response = proxy.receive_request(from_id, timestamp)
            
            # Handling request
            if isinstance(response, list) and response[0] is True:
                _, reply_timestamp = response
                self.receive_reply(to_peer, reply_timestamp)  # Pass timestamp to receive_reply
            else:
                print(f"[RPC Client: {from_id}] ---- Request DENIED by {to_peer} - CS might be busy")

        except Exception as e:
            print(f"[RPC Client: {from_id}] ---- Failed to send request to {to_peer}: {e}")
            
    
    def receive_reply(self, from_pid, timestamp):
        # Update Lamport clock
        self.lamport_clock = max(self.lamport_clock, timestamp) + 1
        self.reply_count += 1
        print(f"[RPC Client: {self.pid}] ---- Received REPLY from Node {from_pid} (ts={timestamp}) ({self.reply_count}/{len(self.peers)})")

        # remove from the queue
        if hasattr(self, 'pending_replies'):
            self.pending_replies.discard(from_pid)

        # enter into critical section if all replies are received
        if self.reply_count == len(self.peers):
            self.enter_critical_section()


    def enter_critical_section(self):
        self.in_critical_section = True
        print(f"[RPC Client: {self.pid}] >>> ENTERING CRITICAL SECTION <<<")
        print("executing critical section....")
        
        # prompt user to exit from critical section
        while self.in_critical_section:
            user_input = input("Do you want to exit from CS and release? (y/n): ").strip().lower()
            if user_input == 'y':
                print(f"[RPC Client: {self.pid}] >>> EXITING CRITICAL SECTION <<<")
                self.in_critical_section = False
                for peer, to_url in self.peers.items():
                    self.send_release(peer, to_url)
            else:
                print(f"[RPC Client: {self.pid}] ---- Staying in CS. Will ask again in 5 seconds.")
                time.sleep(5)
            
    # send release to all peers
    def send_release(self, to_peer, to_url):
        try:
            proxy = xmlrpc.client.ServerProxy(to_url)
            proxy.receive_release(self.pid, self.lamport_clock)
            print(f"[RPC Client: {self.pid}] ---- Sent release to {to_peer}")
        except Exception as e:
            print(f"[RPC Client: {self.pid}] ---- Failed to send release to {to_peer}: {e}")