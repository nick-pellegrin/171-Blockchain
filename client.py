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

            # send user input request to server, converted into bytes
            if user_input.split(" ")[0] == "Transfer":
                global lamport
                lamport += 1
                # print("Lamport clock now <" + str(lamport) + "," + str(idNum) + "> (Transfer Request)")
                requestLamport = lamport

                print("REQUEST <" + str(lamport) + "," + str(idNum) + ">", flush=True)
                # add self to queue
                QUEUE.append((lamport, idNum))
                QUEUE.sort(key=lamportSort)

                # wait until 2 replies have been received
                request_mutex(requestLamport)
                timeoutCounter = 0
                failureFlag = 0
                while (RC[0] != 1 and RC[1] != 1) or (RC[0] != 1 and RC[2] != 1) or (RC[1] != 1 and RC[2] != 1):
                    timeoutCounter += 1
                    sleep(1)
                    if timeoutCounter == 6:
                        print("Mutual Exclusion Failure")
                        failureFlag = 1
                        break
                    continue 

                if failureFlag == 1:
                    continue

                # wait until head of queue is self
                print("QUEUE: " + str(QUEUE))
                while (QUEUE[0][0] != lamport) and (QUEUE[0][1] != idNum):
                    continue

                # now ready to access critical section
                out_sock.sendall(bytes(user_input + " <" + str(requestLamport) + "," + str(idNum) + ">", "utf-8"))
                lamport += 1
                # print("Lamport clock now <" + str(lamport) + "," + str(idNum) + "> (Transfer Performed)")

                # pop from queue and reset RC
                QUEUE.pop(0)
                RC[0] = 0 
                RC[1] = 0
                RC[2] = 0

                lamport += 1
                release_mutex(requestLamport)

            if user_input.split(" ")[0] == "Balance":
                out_sock.sendall(bytes(user_input, "utf-8"))
                lamport += 1
                

    
  
                


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
    global lamport
    data = data.decode()
    data = data.split(" ")
    #print(data)

    receivedID = int(data[0])
    message = data[1]
    receivedLamport = int(data[2])
    
    
    if message == "request":
        lamport = max(lamport, receivedLamport) + 1
        # print("Lamport clock now <" + str(lamport) + "," + str(idNum) + "> (Request Received)")

        print("REPLY <" + str(receivedLamport) + "," + str(receivedID) + "> " + "<" + str(lamport) + "," + str(idNum) + ">")
        QUEUE.append((receivedLamport, receivedID))
        QUEUE.sort(key=lamportSort)
        # print("Request received from P" + str(receivedID))
        # print("Queue: " + str(QUEUE))

        # print(f"Replying to request <" + str(receivedLamport) + ", " + str(receivedID) + ">", flush=True)
        lamport += 1
        # print("Lamport clock now <" + str(lamport) + "," + str(idNum) + "> (Reply Sent)")
        out_sock_dict[receivedID].sendall(bytes(f"{idNum} reply {lamport} {receivedLamport}", "utf-8"))
        sleep(3)
    
    if message == "reply":
        lamport = max(lamport, receivedLamport) + 1

        # print("Lamport clock now <" + str(lamport) + "," + str(idNum) + "> (Reply Received)")
        requestLamport = int(data[3])

        # print("Client P" + str(receivedID) + " replied" + " <" + str(lamport) + ", " + str(idNum) + ">")
        print("REPLIED <" + str(requestLamport) + "," + str(idNum) + "> " + "<" + str(receivedLamport) + "," + str(receivedID) + ">")
        RC[receivedID - 1] = 1
    
    if message == "release":
        requestLamport = int(data[3])
        lamport = max(lamport, receivedLamport) + 1
        # print("Lamport clock now <" + str(lamport) + "," + str(idNum) + "> (Release Received)")

        print("DONE <" + str(requestLamport) + "," + str(receivedID) + ">")
        # print(f"Releasing <" + str(receivedLamport) + ", " + str(receivedID) + ">", flush=True)
        QUEUE.pop(0)


def request_mutex(requestLamport):
    sleep(3)
    # print("Requesting <" + str(lamport) + ", " + str(idNum) + ">", flush=True)
    for client in out_sock_dict.values():
        client.sendall(bytes(f"{idNum} request {requestLamport}", "utf-8"))
        sleep(3)

def release_mutex(requestLamport):
    sleep(3)
    # print("Releasing <" + str(lamport) + ", " + str(idNum) + ">", flush=True)
    print("RELEASE <" + str(requestLamport) + "," + str(idNum) + ">")
    for client in out_sock_dict.values():
        client.sendall(bytes(f"{idNum} release {lamport} {requestLamport}", "utf-8"))
        sleep(3)
    

# this sorts the queue by lamport time ascending, then by process number descending
def lamportSort(pair):
    return (pair[0], pair[1])

def handle_request(data1, data2):
    pass


# -----------------------------------------------------------------------------------------------------------------

    

    


if __name__ == "__main__":
    
    # INITIALIZE CLIENT -------------------------------------------------------------
    sleep(1) # sleep for 1sec upon process start to allow server to start first
    id = str(sys.argv[1])
    idNum = int([*id][1])

    # initialize mutext variables
    # global lamport
    lamport = 0
    RC = [0, 0, 0] # REPLY COUNTER
    QUEUE = []


    # define client IP address and port number
    CLIENT_IP = socket.gethostname()
    CLIENT_PORT = 9000 + idNum

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


    sleep(8)
    out_sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out_sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if CLIENT_PORT == 9001:
        out_sock1.connect((CLIENT_IP, 9002))
        out_sock_dict[2] = out_sock1
        # print(f"connected to client P2", flush=True)
        out_sock2.connect((CLIENT_IP, 9003))
        out_sock_dict[3] = out_sock2
        # print(f"connected to client P3", flush=True)
    if CLIENT_PORT == 9002:
        out_sock1.connect((CLIENT_IP, 9001))
        out_sock_dict[1] = out_sock1
        # print(f"connected to client P1", flush=True)
        out_sock2.connect((CLIENT_IP, 9003))
        out_sock_dict[3] = out_sock2
        # print(f"connected to client P3", flush=True)
    if CLIENT_PORT == 9003:
        out_sock1.connect((CLIENT_IP, 9001))
        out_sock_dict[1] = out_sock1
        # print(f"connected to client P1", flush=True)
        out_sock2.connect((CLIENT_IP, 9002))
        out_sock_dict[2] = out_sock2
        # print(f"connected to client P2", flush=True)
    
    # -------------------------------------------------------------------------------





    # spawn a new thread to handle continuous user input
    threading.Thread(target=get_user_input).start()

    # spawn a new thread to handle continuous server response
    threading.Thread(target=respond_to_server).start()

    # thread for handling mutex requests done after accepting inbound connection
