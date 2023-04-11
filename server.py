import socket
import threading

from os import _exit
from sys import stdout
from time import sleep

# terminate program upon any user input
def get_user_input():
	input()
	# close all sockets before exiting
	in_sock.close()
	for sock in out_socks:
		sock[0].close()
	print("exiting program", flush=True)
	stdout.flush()
	_exit(0)

# simulates network delay then handles received message
def handle_msg(data, addr):
	sleep(3) 
	data = data.decode() # decode byte data into a string
	print(f"{addr[1]}: {data}", flush=True) # echo message to console

	# broadcast to all clients by iterating through each stored connection
	for sock in out_socks:
		conn = sock[0]
		recv_addr = sock[1]
		# echo message back to client
		try:
			# convert message into bytes and send through socket
			conn.sendall(bytes(f"{addr[1]}: {data}", "utf-8"))
			print(f"sent message to port {recv_addr[1]}", flush=True)
		# handling exception in case trying to send data to a closed connection
		except:
			print(f"exception in sending to port {recv_addr[1]}", flush=True)
			continue

# handle a new connection by waiting to receive from connection
def respond(conn, addr):
	print(f"accepted connection from port {addr[1]}", flush=True)

	# infinite loop to keep waiting to receive new data from this client
	while True:
		try:
			# wait to receive new data, 1024 is receive buffer size
			data = conn.recv(1024)

		except:
			print(f"exception in receiving from {addr[1]}", flush=True)
			break
			
		if not data:
			# close own socket to client since other end is closed
			conn.close()
			print(f"connection closed from {addr[1]}", flush=True)
			break

		# spawn a new thread to handle message 
		threading.Thread(target=handle_msg, args=(data, addr)).start()

if __name__ == "__main__":

	IP = socket.gethostname()
	PORT = 9000

	# create a socket object, SOCK_STREAM specifies a TCP socket
	in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	in_sock.bind((IP, PORT))
	in_sock.listen()

	# container to store all connections
	out_socks = []
	
	threading.Thread(target=get_user_input).start() # spawn a new thread to wait for user input

	# infinite loop to keep accepting new connections
	while True:
		try:
			# conn: socket object used to send to and receive from connection
			# addr: (IP, port) of connection 
			conn, addr = in_sock.accept()
		except:
			print("exception in accept", flush=True)
			break
		# add connection to array to send data through it later
		out_socks.append((conn, addr))
		# spawn new thread for responding to each connection
		threading.Thread(target=respond, args=(conn, addr)).start()
