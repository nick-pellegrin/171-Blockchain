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
        else:
            try:
                # send user input request to server, converted into bytes
                if user_input.split(" ")[0] == "Transfer":
                    global lamport
                    lamport = lamport + 1
                    request_mutex()
                    out_sock.sendall(bytes(user_input, "utf-8"))
                    release_mutex()

                if user_input.split(" ")[0] == "Balance":
                    out_sock.sendall(bytes(user_input, "utf-8"))
                

    
            except:
                # handling exception in case trying to send data to a closed connection
                print("exception in sending to server")
                continue
                
            # print("request sent to server")


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
        inbound_socks.append((conn, addr))
        print("connected to inbound client", flush=True)
        threading.Thread(target=listen, args=(conn, addr)).start()
        #threading.Thread(target=respond_to_client, args=(conn,)).start() # spawn a new thread to handle client ***********************
# -----------------------------------------------------------------------------------------------------------------


# HANDLE MUTUAL EXCLUSION -----------------------------------------------------------------------------------------
def listen(conn, addr):
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
        threading.Thread(target=respond, args=(data, conn, addr)).start()


def respond(data, conn, addr):
    data = data.decode()
    data = data.split(" ")
    #print(data)
    global lamport
    
    if data[1] == "request":
        lamport = max(lamport, int(data[2]))
        print(f"REQUEST RECEIVED, SENDING REPLY <" + str(lamport) + ", " + str(id) + ">", flush=True)
        out_sock_dict[int(data[0])].sendall(bytes(f"{9000 + int([*id][1])} reply", "utf-8"))
    
    if data[1] == "reply":
        #lock -= 1
        print("REPLY RECEIVED <" + str(lamport) + ", " + str(id) + ">")
        #lamport = max(lamport, int(data[2])) + 1
    
    if data[1] == "release":
        print(f"RELEASE RECEIVED <" + str(lamport) + ", " + str(id) + ">", flush=True)
        lock = 2
    


def request_mutex():
    sleep(3)
    print("REQUESTING <" + str(lamport) + ", " + str(id) + ">", flush=True)
    for client in out_sock_dict.values():
        client.sendall(bytes(f"{9000 + int([*id][1])} request {lamport}", "utf-8"))
def release_mutex():
    sleep(3)
    print("RELEASING <" + str(lamport) + ", " + str(id) + ">", flush=True)
    for client in out_sock_dict.values():
        client.sendall(bytes(f"{9000 + int([*id][1])} release {lamport}", "utf-8"))


def handle_request(data1, data2):
    pass
# -----------------------------------------------------------------------------------------------------------------

    

    


if __name__ == "__main__":
    
    # INITIALIZE CLIENT -------------------------------------------------------------
    sleep(1) # sleep for 1sec upon process start to allow server to start first
    id = str(sys.argv[1])

    # initialize mutext variables
    global lamport
    lamport = 0
    lock = 2
    REQUEST_QUEUE = []


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
    out_sock_dict = {}
    inbound_socks = []
    

    # spawn a new thread to handle incoming connections from other clients
    threading.Thread(target=get_connections).start()


    sleep(5)
    out_sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out_sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if CLIENT_PORT == 9001:
        MY_ID = 1
        out_sock1.connect((CLIENT_IP, 9002))
        out_sock_dict[9002] = out_sock1
        print(f"connected to client P2", flush=True)
        out_sock2.connect((CLIENT_IP, 9003))
        out_sock_dict[9003] = out_sock2
        print(f"connected to client P3", flush=True)
    if CLIENT_PORT == 9002:
        MY_ID = 2
        out_sock1.connect((CLIENT_IP, 9001))
        out_sock_dict[9001] = out_sock1
        print(f"connected to client P1", flush=True)
        out_sock2.connect((CLIENT_IP, 9003))
        out_sock_dict[9003] = out_sock2
        print(f"connected to client P3", flush=True)
    if CLIENT_PORT == 9003:
        MY_ID = 3
        out_sock1.connect((CLIENT_IP, 9001))
        out_sock_dict[9001] = out_sock1
        print(f"connected to client P1", flush=True)
        out_sock2.connect((CLIENT_IP, 9002))
        out_sock_dict[9002] = out_sock2
        print(f"connected to client P2", flush=True)
    
    # -------------------------------------------------------------------------------





    # spawn a new thread to handle continuous user input
    threading.Thread(target=get_user_input).start()

    # spawn a new thread to handle continuous server response
    threading.Thread(target=respond_to_server).start()

    # thread for handling mutex requests done after accepting inbound connection
