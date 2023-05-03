import socket
import threading
import pickle

from os import _exit
from sys import stdout
from time import sleep
from blockchain import Blockchain
from blockchain import Block

# keep waiting for user inputs
def get_user_input():
    while True:
        # wait for user input
        user_input = input()
        if user_input == "exit":
            in_sock.close()
            for sock in out_socks:
                sock[0].close()
            print("exiting program", flush=True)
            stdout.flush()
            _exit(0)
        if user_input.split(" ")[0] == "wait":
            print("program waiting for " + user_input.split(" ")[1] + " seconds")
            sleep(int(user_input.split(" ")[1]))
        else:
            try:
                if user_input == "Blockchain":
                    bc = blockchain.get_chain()
                    if len(bc) > 1:
                        out_str = '['
                        for block in bc[1:]:
                            out_str += f'({block[0]}, {block[1]}, ${block[2]}, {block[3]}), '
                        out_str = out_str[:-2] + ']' # remove last comma+space and add closing bracket
                    elif len(bc) == 1:
                        out_str = '[]' # empty condition
                    print(out_str, flush=True)

                if user_input == "Balance":
                    # for client in IDS.values():
                    #     print(f"{client}: {blockchain.get_balance(client)}", flush=True)
                    P1_balance = blockchain.get_balance("P1")
                    P2_balance = blockchain.get_balance("P2")
                    P3_balance = blockchain.get_balance("P3")
                    print(f"P1: ${P1_balance}, P2: ${P2_balance}, P3: ${P3_balance}", flush=True)
    
            except:
                # handling exception in case trying to send data to a closed connection
                print("exception in reading from user - 123", flush=True)
                continue
    


# simulates network delay then handles received message
def handle_msg(data, conn, addr):
    sleep(3) 
    data = data.decode() # decode byte data into a string
    data = data.split(" ")
    try:
        if data[0] == "Balance": # ['Balance', client process]
            balance = blockchain.get_balance(data[1])
            #print(f"handling balance request from {IDS[conn]}", flush=True)
            conn.sendall(bytes(f"Balance: ${balance}", "utf-8"))
        if data[0] == "Transfer": # ['Transfer', recipient process, amount]
            if blockchain.get_balance(IDS[conn]) >= int(data[2].replace("$", "")):
                #print(f"handling transfer request of {data[2]}: {IDS[conn]} -> {data[1]}", flush=True)
                new_block = Block(blockchain.get_latest_block().hash, IDS[conn], data[1], int(data[2].replace("$", "")))
                blockchain.add_block(new_block)
                conn.sendall(bytes(f"Success", "utf-8"))
            else:
                #print(f"insufficient funds for transaction of {data[2]}: {IDS[conn]} -> {data[1]}", flush=True)
                conn.sendall(bytes(f"Insufficient Balance", "utf-8"))
    except:
        pass
        #print(f"exception in handling request", flush=True)



# handle a new connection by waiting to receive from connection
def respond(conn, addr):
    # receive client process ID
    init_data = conn.recv(1024).decode()
    IDS[conn] = str(init_data)
    print(f"accepted connection from client {IDS[conn]}", flush=True)
    if len(IDS) == 3:
        print("all clients connected", flush=True)
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
        threading.Thread(target=handle_msg, args=(data, conn, addr)).start()



if __name__ == "__main__":

    # Initialize global Blockchain
    blockchain = Blockchain()

    # Initialize connection IDs
    IDS = {}

    IP = socket.gethostname()
    PORT = 9000

    # create a socket object, SOCK_STREAM specifies a TCP socket
    in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    in_sock.bind((IP, PORT))
    in_sock.listen()

    # container to store all connections
    out_socks = []
    
    # spawn a new thread to wait for user input
    threading.Thread(target=get_user_input).start() 


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
