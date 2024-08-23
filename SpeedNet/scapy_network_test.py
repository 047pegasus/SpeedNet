
from scapy.all import *
import threading
import time
import os
import msvcrt

def send_packet_tcp(ip, port, packet):
    try:
        send(IP(dst=ip)/TCP(dport=port)/packet)
    except Exception as e:
        print(f"Failed to send TCP packet: {e}")

def send_packet_udp(ip, port, packet):
    try:
        send(IP(dst=ip)/UDP(dport=port)/packet)
    except Exception as e:
        print(f"Failed to send UDP packet: {e}")

def write_to_file(data):
    filename = 'transfer_log.txt'
    try:
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(data)
        else:
            with open(filename, 'a') as f:
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, len(data))
                f.write(data)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, len(data))
    except Exception as e:
        print(f"Failed to write to log file: {e}")

def send_file_tcp(ip, port):
    filename = 'file.txt'
    try:
        with open(filename, 'wb') as f:
            f.write(os.urandom(1024*1024))
        with open(filename, 'rb') as f:
            packet = f.read(1024)
            while packet:
                send_packet_tcp(ip, port, packet)
                packet = f.read(1024)
        os.remove(filename)
    except Exception as e:
        print(f"Failed to send TCP file: {e}")

def send_file_udp(ip, port):
    filename = 'file.txt'
    try:
        with open(filename, 'wb') as f:
            f.write(os.urandom(1024*1024))
        with open(filename, 'rb') as f:
            packet = f.read(1024)
            while packet:
                send_packet_udp(ip, port, packet)
                packet = f.read(1024)
        os.remove(filename)
    except Exception as e:
        print(f"Failed to send UDP file: {e}")


def tcp_thread():
    ip = 'localhost'
    port = 123
    packet = b'Hello World'
    
    start = time.time()
    send_packet_tcp(ip, port, packet)
    end = time.time()
    bandwidth = len(packet)/(end-start)/1024/1024
    data = f'TCP Bandwidth: {bandwidth} MB/s\n'
    write_to_file(data)
    
    start = time.time()
    send_file_tcp(ip, port)
    end = time.time()
    bandwidth = 1/(end-start)
    data = f'TCP File Transfer Bandwidth: {bandwidth} MB/s\n'
    write_to_file(data)

def udp_thread():
    ip = 'localhost'
    port = 123
    packet = b'Hello World'
    
    start = time.time()
    send_packet_udp(ip, port, packet)
    end = time.time()
    bandwidth = len(packet)/(end-start)/1024/1024
    data = f'UDP Bandwidth: {bandwidth} MB/s\n'
    write_to_file(data)
    
    start = time.time()
    send_file_udp(ip, port)
    end = time.time()
    bandwidth = 1/(end-start)
    data = f'UDP File Transfer Bandwidth: {bandwidth} MB/s\n'
    write_to_file(data)

def main():
    tcp = threading.Thread(target=tcp_thread)
    udp = threading.Thread(target=udp_thread)
    
    tcp.start()
    udp.start()
    
    tcp.join()
    udp.join()

if __name__ == '__main__':
    main()

