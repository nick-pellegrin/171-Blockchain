import socket
import threading
import sys


from os import _exit
from sys import stdout
from time import sleep

# keep waiting and asking for user inputs
def get_user_input():
    while True:
        # wait for user input
        user_input = input()
        if user_input == "exit":
            out_sock.close()
            #print("exiting program")
            stdout.flush()
            _exit(0)
        if user_input.split(" ")[0] == "wait":
            print("program waiting for " + user_input.split(" ")[1] + " seconds")
            sleep(int(user_input.split(" ")[1]))
        if user_input.split(" ")[0] == "hi":
            # for client in client_socks:
            #     client.sendall(bytes(f"HIIIIIIII", "utf-8"))
            out_sock1.sendall(bytes(f"hi", "utf-8"))
            out_sock2.sendall(bytes(f"hi", "utf-8"))
        else:
            try:
                # send user input request to server, converted into bytes
                # request_mutex()
                # while LOCK != 0:
                #     print(LOCK)
                #     continue
                out_sock.sendall(bytes(user_input, "utf-8"))
                # release_mutex()
                pass

    
            except:
                # handling exception in case trying to send data to a closed connection
                print("exception in sending to server")
                continue
                
            print("request sent to server")


def respond_to_server():
    # infinite loop to keep waiting to receive new data from server
    while True:
        try:
            data = out_sock.recv(1024) # 1024 is receive buffer size
        except:
            print("exception in receiving")
            break
        if not data:
            # close own socket since other end is closed
            out_sock.close()
            print("connection closed from server")
            break

        # spawn a new thread to handle message
        threading.Thread(target=handle_msg, args=(data,)).start()


# simulates network delay then handles received message
def handle_msg(data):
    sleep(3)
    data = data.decode() # decode byte data into a string
    print(data) # echo message to console



# HANDLE MAKING/RECIEVING CONNECTIONS ----------------------------------------------------------------------------
def get_connections():
    while True:
        try:
            conn, addr = in_sock.accept()
        except:
            print("exception in accept", flush=True)
            break
        client_socks.append(conn)
        print("connected to inbound client", flush=True)
        threading.Thread(target=listen, args=(conn,)).start()
        #threading.Thread(target=respond_to_client, args=(conn,)).start() # spawn a new thread to handle client ***********************


# def make_connections(port):
#     # after making a successful outbound connection to another client,
#     # we do not store that connection, as connections to other clients
#     # are stored on the inbound side, we just need to make the outbound
#     # connection so the other client can store the connection on inbound
#     out_sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     while True:
#         try:
#             out_sock_client.connect((CLIENT_IP, port))
#             print(f"connected to client P{port - 9000}", flush=True)
#             #break
#         except:
#             #print("exception in making outbound connection to client", flush=True)
#             continue
#     return out_sock_client
# -----------------------------------------------------------------------------------------------------------------


# HANDLE MUTUAL EXCLUSION -----------------------------------------------------------------------------------------
def listen(conn):
# infinite loop to keep waiting to receive new data from this client
    while True:
        try:
            # wait to receive new data, 1024 is receive buffer size
            data = conn.recv(1024)
        except:
            print(f"exception in receiving from {conn}", flush=True)
            break
            
        if not data:
            # close own socket to client since other end is closed
            conn.close()
            print(f"connection closed from {conn}", flush=True)
            break

        # spawn a new thread to handle message 
        threading.Thread(target=handle_msg, args=(data,)).start()

# def respond_to_client(client_sock):
#     # infinite loop to keep waiting to receive new data from a client
#     while True:
#         try:
#             data = client_sock.recv(1024) # 1024 is receive buffer size
#         except:
#             print("exception in receiving")
#             break
#         if not data:
#             # close own socket since other end is closed
#             client_sock.close()
#             print("connection closed from client")
#             break
#         if data.decode()[1] == "request":
#             #REQUEST_QUEUE.append((client_sock, data.decode()[2])) # (socket, timestamp)
#             #sock = REQUEST_QUEUE.pop(0)
#             print(f"REPLY {data.decode()[2]} {LAMPORT}", flush=True)
#             LAMPORT = max(LAMPORT, data.decode()[2]) + 1
#             client_sock.sendall(bytes(f"P{id} reply {data.decode()[2]} {LAMPORT}", "utf-8"))
#         if data.decode()[1] == "reply":
#             LOCK -= 1
#             print(f"REPLIED {data.decode()[2]} {LAMPORT}", flush=True)
#             LAMPORT = max(LAMPORT, data.decode()[2]) + 1
#         if data.decode()[1] == "release":
#             print(f"DONE {data.decode()[2]}", flush=True)
#             LOCK = 2

# def request_mutex():
#     for client in client_socks:
#         client.sendall(bytes(f"P{id} request {LAMPORT}", "utf-8"))

# def release_mutex():
#     for client in client_socks:
#         client.sendall(bytes(f"P{id} release {LAMPORT}", "utf-8"))


# def handle_request(data1, data2):
#     pass
# -----------------------------------------------------------------------------------------------------------------

    

    


if __name__ == "__main__":
    
    # INITIALIZE CLIENT -------------------------------------------------------------
    sleep(1) # sleep for 1sec upon process start to allow server to start first
    id = str(sys.argv[1])

    # initialize mutext variables
    LAMPORT = 0
    REQUEST_QUEUE = []
    global LOCK
    LOCK = 2


    # define client IP address and port number
    CLIENT_IP = socket.gethostname()
    CLIENT_PORT = 9000 + int([*id][1])

    # get server's IP address and port number
    SERVER_IP = socket.gethostname()
    SERVER_PORT = 9000
    # -------------------------------------------------------------------------------



    # CONNECT TO SERVER -------------------------------------------------------------
    # create outbound connection to server
    out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out_sock.connect((SERVER_IP, SERVER_PORT))
    print("connected to server")
    out_sock.sendall(bytes(id, "utf-8"))
    # -------------------------------------------------------------------------------



    # CONECT TO OTHER CLIENTS -------------------------------------------------------
    # create an inbound socket object, SOCK_STREAM specifies a TCP socket
    in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    in_sock.bind((CLIENT_IP, CLIENT_PORT))
    in_sock.listen()

    # container to store all client connections
    client_socks = []

    # spawn a new thread to handle incoming connections from other clients
    threading.Thread(target=get_connections).start()

    # create outbound connections to other clients
    # if CLIENT_PORT == 9001:
    #     out_sock1 = threading.Thread(target=make_connections, args=(9002,)).start()
    #     out_sock2 = threading.Thread(target=make_connections, args=(9003,)).start()
    #     #out_socks = [out_sock2, out_sock3]
    # if CLIENT_PORT == 9002:
    #     out_sock1 = threading.Thread(target=make_connections, args=(9001,)).start()
    #     out_sock2 = threading.Thread(target=make_connections, args=(9003,)).start()
    #     #out_socks = [out_sock1, out_sock3]
    # if CLIENT_PORT == 9003:
    #     out_sock1 = threading.Thread(target=make_connections, args=(9001,)).start()
    #     out_sock2 = threading.Thread(target=make_connections, args=(9002,)).start()
    #     #out_socks = [out_sock1, out_sock2]

    sleep(8)
    out_sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out_sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if CLIENT_PORT == 9001:
        out_sock1.connect((CLIENT_IP, 9002))
        print(f"connected to client P2", flush=True)
        out_sock2.connect((CLIENT_IP, 9003))
        print(f"connected to client P3", flush=True)
    if CLIENT_PORT == 9002:
        out_sock1.connect((CLIENT_IP, 9001))
        print(f"connected to client P2", flush=True)
        out_sock2.connect((CLIENT_IP, 9003))
        print(f"connected to client P3", flush=True)
    if CLIENT_PORT == 9003:
        out_sock1.connect((CLIENT_IP, 9001))
        print(f"connected to client P2", flush=True)
        out_sock2.connect((CLIENT_IP, 9002))
        print(f"connected to client P3", flush=True)
    # -------------------------------------------------------------------------------





    # spawn a new thread to handle continuous user input
    threading.Thread(target=get_user_input).start()

    # spawn a new thread to handle continuous server response
    threading.Thread(target=respond_to_server).start()

    # spawn a new thread to listen for continuous client messages
    # for conn in client_socks:
    #     threading.Thread(target=listen, args=(conn,)).start()

    # thread for handling mutex requests done after accepting inbound connection
