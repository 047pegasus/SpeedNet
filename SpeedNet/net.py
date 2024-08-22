# program to generate a small network packet using AFI NET and send it to a given IP address using python usockets and measure the bandwidth of the transmission. The program should also keep a log of the transfer in a separate file called transfer_log.txt. Before writing the result to the file, it should check if the file exists or not. If it does not exist, it should create the file and also check if the file is being used by any other program to write, then it must wait until it acquires the lock and then it shall start to write.

import socket
import time
import os
import fcntl

def send_packet(ip, port, packet):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(packet, (ip, port))
    s.close()
    
def write_to_file(data):
    filename = 'transfer_log.txt'
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write(data)
    else:
        with open(filename, 'a') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(data)
            fcntl.flock(f, fcntl.LOCK_UN)

#function to genrate a small file of size 1MB and send it to the given IP address using sockets
def send_file(ip, port):
    filename = 'file.txt'
    with open(filename, 'wb') as f:
        f.write(os.urandom(1024*1024))
    with open(filename, 'rb') as f:
            packet = f.read(1024)
            while packet:
                send_packet(ip, port, packet)
                packet = f.read(1024)
    os.remove(filename)

def main():
    ip = 'localhost'
    port = 123
    packet = b'Hello World'

    start = time.time()
    send_packet(ip, port, packet)
    end = time.time()
    #calculate bandwidth in MB/s
    bandwidth = len(packet)/(end-start)/1024/1024
    data = f'Bandwidth: {bandwidth}\n'
    write_to_file(data)
    start = time.time()
    send_file(ip, port)
    end = time.time()
    #calculate bandwidth in MB/s
    bandwidth = 1/(end-start)
    data = f'Bandwidth: {bandwidth}\n'
    write_to_file(data)


if __name__ == '__main__':
    main()


