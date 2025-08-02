# Process 1 - Node

import time
import xmlrpc.client

class Node:
    def __init__(self, pid, peers):
        self.pid = pid
        self.peers = peers
        self.lamport_clock = 0
        self.reply_count = 0
        self.pending_replies = set()
        self.in_critical_section = False
        
    def increment_clock(self):
        self.lamport_clock += 1

    def receive_request(self, from_pid, timestamp):
        self.lamport_clock = max(self.lamport_clock, timestamp)
        self.increment_clock()

        if self.in_critical_section:
            print(f"[RPC Client: {self.pid}] ---- Received REQUEST from Node {from_pid} while in CS! Denying access")
            return False
        else:
            print(f"[RPC Client: {self.pid}] ---- Received REQUEST from Node {from_pid} (ts={timestamp}), replying")
            return True

    def receive_release(self, from_pid):
        print(f"[RPC Client: {self.pid}] ---- Received RELEASE from Node {from_pid}")
        return True
    
    def request_critical_section(self):
        if self.in_critical_section:
            print(f"[RPC Client: {self.pid}] Already in CS, cannot request again.")
            return
    
        self.increment_clock()
        ts = self.lamport_clock
        self.reply_count = 0
        print(f"[RPC Client: {self.pid}] ---- Requesting CS with timestamp {ts}")
        
        self.pending_replies = set(self.peers.keys())

        while self.reply_count < len(self.peers):
            for peer in list(self.pending_replies):
                to_url = self.peers[peer]
                try:
                    self.send_request(to_url, peer, self.pid, ts)
                except Exception as e:
                    print(f"[RPC Client: {self.pid}] ---- Failed to contact {peer}: {e}")

            if self.reply_count < len(self.peers):
                print(f"[RPC Client: {self.pid}] ---- Waiting... Will retry for: {self.pending_replies}")
                time.sleep(2)
    
    def send_request(self, to_url, to_peer, from_id, timestamp):
        try:
            proxy = xmlrpc.client.ServerProxy(to_url)
            response = proxy.receive_request(from_id, timestamp)
            
            if response is True:
                self.receive_reply(to_peer)
            else:
                print(f"[RPC Client: {from_id}] ---- Request DENIED by {to_peer} - CS might be busy")

        except Exception as e:
            print(f"[RPC Client: {from_id}] ---- Failed to send request to {to_peer}: {e}")
            
    
    def receive_reply(self, from_pid):
        self.reply_count += 1
        print(f"[RPC Client: {self.pid}] ---- Received reply from Node {from_pid} ({self.reply_count}/{len(self.peers)})")

        if hasattr(self, 'pending_replies'):
            self.pending_replies.discard(from_pid)

        if self.reply_count == len(self.peers):
            self.enter_critical_section()

        return True
    
    def enter_critical_section(self):
        self.in_critical_section = True
        print(f"[RPC Client: {self.pid}] >>> ENTERING CRITICAL SECTION <<<")
        print("executing critical section....")
        
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
            
    def send_release(self, to_peer, to_url):
        try:
            proxy = xmlrpc.client.ServerProxy(to_url)
            proxy.receive_release(self.pid)
            print(f"[RPC Client: {self.pid}] ---- Sent release to {to_peer}")
        except Exception as e:
            print(f"[RPC Client: {self.pid}] ---- Failed to send release to {to_peer}: {e}")