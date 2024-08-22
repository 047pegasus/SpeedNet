# program to generate a random file of a given size and transfer it to a given IP address using python usockets and measure the bandwidth of the transmission. The program should also keep a log of the transfer in a separate file called transfer_log.txt. Before writing the result to the file, it should check if the file exists or not. If it does not exist, it should create the file and also check if the file is being used by any other program to write, then it must wait until it acquires the lock and then it shall start to write.

import os
import time
import platform
import threading
import socket
import random
import string

def generate_random_file(file_name, size):
    with open(file_name, "w") as file:
        file.write("Hello transmit".join(random.choices(string.ascii_lowercase, k=size)))
                   
def transfer_file(file_name, ip):
    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # bind the socket to the ip address and port
    s.bind((ip, 1234))
    
    # listen for incoming connections
    s.listen(5)
    
    # accept the connection
    c, addr = s.accept()
    
    # send the file
    with open(file_name, "r") as file:
        data = file.read(1024)
        while data:
            c.send(data)
            data = file.read(1024)
    
    # close the connection
    c.close()
    
    # close the socket
    s.close()

def write_to_file(file_name, data):
    while os.path.exists(file_name):
        try:
            with open(file_name, "a") as file:
                file.write(data)
                file.write("\n")
                break
        except:
            time.sleep(1)
    else:
        with open(file_name, "w") as file:
            file.write(data)
            file.write("\n")

generate_random_file("random_file.txt", 1024)

# accept_thread = threading.Thread(target= accept_file, args=("127.0.0.1"))
# accept_thread.start()
# accept_thread.join()
# accept_file("127.0.0.1")

transfer_file("random_file.txt", "localhost")
thread = threading.Thread(target=write_to_file, args=("transfer_log.txt", "File transfer complete"))
thread.start()
thread.join()