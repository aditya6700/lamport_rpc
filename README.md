# Lamport's Distributed Mutual Exclusion using RPC

This project implements **Lamport’s Mutual Exclusion Algorithm** using **Python** and **XML-RPC** to coordinate access to a shared **Critical Section (CS)** among three distributed processes.

---

## Overview
- **Processes:** P1, P2, P3  
- **Algorithm:** Lamport's Logical Clocks for ordering requests.  
- **Communication:** XML-RPC for remote method calls between processes.  
- **Goal:** Ensure that only one process enters the CS at any given time, while others wait or queue requests.

---

## Features
- Logical clock updates on message send/receive.
- Queueing of requests when CS is busy.
- Deferred replies based on timestamp ordering.
- Retry mechanism for unresponsive peers.
- Real-time simulation of distributed coordination.

---

## How It Works
1. **Request CS:** Process increments Lamport clock and sends `REQUEST` to peers.
2. **Reply Handling:** Peers reply immediately or defer if in CS or queued.
3. **Enter CS:** Process enters CS after receiving all required replies.
4. **Release CS:** Process sends `RELEASE` to peers, triggering queued requests.
5. **Ordering:** All events follow Lamport's logical time ordering.

---
