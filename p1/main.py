# Process 1 - Main

import server
from config import PORT
import node
import time

if __name__ == "__main__":
    server.start_server(PORT)

    time.sleep(2)  # Let others start

    # Simulate critical section request after some time
    node.request_critical_section()
