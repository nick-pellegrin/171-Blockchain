import socket
import threading

from os import _exit
from sys import stdout
from time import sleep

# keep waiting and asking for user inputs
def get_user_input():
    while True:
        # wait for user input
        user_input = input()
        if user_input == "":
            out_sock.close()
            print("exiting program")
            stdout.flush()
            _exit(0)
        else:
            try:
                # send user input string to server, converted into bytes
                out_sock.sendall(bytes(user_input, "utf-8"))
    
            except:
                # handling exception in case trying to send data to a closed connection
                print("exception in sending to server")
                continue
                
            print("sent latest input to server")

# simulates network delay then handles received message
def handle_msg(data):
    sleep(3)
    data = data.decode() # decode byte data into a string
    print(data) # echo message to console

if __name__ == "__main__":
    
    # predefine client ID
    CLIENT_ID = "P1"

    # get server's IP address and port number
    SERVER_IP = socket.gethostname()
    SERVER_PORT = 9000

    # create a socket object, SOCK_STREAM specifies a TCP socket
    # do not need to specify address for own socket for making an outbound connection
    out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # attempt to connect own socket to server's socket address
    out_sock.connect((SERVER_IP, SERVER_PORT))
    print("connected to server")

    # spawn a new thread to handle continuous user input
    threading.Thread(target=get_user_input).start()


    # infinite loop to keep waiting to receive new data from server
    while True:
        try:
            data = out_sock.recv(1024) # 1024 is receive buffer size
        
        # handle exception in case something happened to connection
        except:
            print("exception in receiving")
            break
        if not data:
            # close own socket since other end is closed
            out_sock.close()
            print("connection closed from server")
            break

        # spawn a new thread to handle message 
        # so simulated network delay and message handling don't block receive
        threading.Thread(target=handle_msg, args=(data,)).start()
