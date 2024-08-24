# from scapy.all import *
# import threading
# import time
# import os
# import msvcrt

# # Function to send a TCP packet to the specified IP and port
# def send_packet_tcp(ip, port, packet):
#     try:
#         send(IP(dst=ip)/TCP(dport=port)/packet)
#     except Exception as e:
#         print(f"Failed to send TCP packet: {e}")

# # Function to send a UDP packet to the specified IP and port
# def send_packet_udp(ip, port, packet):
#     try:
#         send(IP(dst=ip)/UDP(dport=port)/packet)
#     except Exception as e:
#         print(f"Failed to send UDP packet: {e}")

# # Function to write data to a log file with file locking
# def write_to_file(data):
#     filename = 'transfer_log.txt'
#     try:
#         if not os.path.exists(filename):
#             with open(filename, 'w') as f:
#                 f.write(data)
#         else:
#             with open(filename, 'a') as f:
#                 msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, len(data))
#                 f.write(data)
#                 msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, len(data))
#     except Exception as e:
#         print(f"Failed to write to log file: {e}")

# # Function to create a 1MB file and send it in chunks over TCP
# def send_file_tcp(ip, port):
#     filename = 'file.txt'
#     try:
#         with open(filename, 'wb') as f:
#             f.write(os.urandom(1024*1024))  # Generate 1MB random file
#         with open(filename, 'rb') as f:
#             packet = f.read(1024)
#             while packet:
#                 send_packet_tcp(ip, port, packet)
#                 packet = f.read(1024)
#         os.remove(filename)
#     except Exception as e:
#         print(f"Failed to send TCP file: {e}")

# # Function to create a 1MB file and send it in chunks over UDP
# def send_file_udp(ip, port):
#     filename = 'file.txt'
#     try:
#         with open(filename, 'wb') as f:
#             f.write(os.urandom(1024*1024))  # Generate 1MB random file
#         with open(filename, 'rb') as f:
#             packet = f.read(1024)
#             while packet:
#                 send_packet_udp(ip, port, packet)
#                 packet = f.read(1024)
#         os.remove(filename)
#     except Exception as e:
#         print(f"Failed to send UDP file: {e}")

# # Thread function for TCP operations: send a packet, send a file, and log bandwidth
# def tcp_thread():
#     ip = 'localhost'
#     port = 123
#     packet = b'Hello World'
    
#     start = time.time()
#     send_packet_tcp(ip, port, packet)
#     end = time.time()
#     bandwidth = len(packet)/(end-start)/1024/1024
#     data = f'TCP Bandwidth: {bandwidth} MB/s\n'
#     write_to_file(data)
    
#     start = time.time()
#     send_file_tcp(ip, port)
#     end = time.time()
#     bandwidth = 1/(end-start)
#     data = f'TCP File Transfer Bandwidth: {bandwidth} MB/s\n'
#     write_to_file(data)

# # Thread function for UDP operations: send a packet, send a file, and log bandwidth
# def udp_thread():
#     ip = 'localhost'
#     port = 123
#     packet = b'Hello World'
    
#     start = time.time()
#     send_packet_udp(ip, port, packet)
#     end = time.time()
#     bandwidth = len(packet)/(end-start)/1024/1024
#     data = f'UDP Bandwidth: {bandwidth} MB/s\n'
#     write_to_file(data)
    
#     start = time.time()
#     send_file_udp(ip, port)
#     end = time.time()
#     bandwidth = 1/(end-start)
#     data = f'UDP File Transfer Bandwidth: {bandwidth} MB/s\n'
#     write_to_file(data)

# # Main function to start TCP and UDP threads and wait for them to finish
# def main():
#     tcp = threading.Thread(target=tcp_thread)
#     udp = threading.Thread(target=udp_thread)
    
#     tcp.start()
#     udp.start()
    
#     tcp.join()
#     udp.join()

# if __name__ == '__main__':
#     main()


from scapy.all import *
import threading
import time
import os
import msvcrt

# Function to get the directory of the current script
def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

# Function to write data to a log file with file locking
def write_to_file(data):
    script_dir = get_script_dir()
    filename = os.path.join(script_dir, 'transfer_log.txt')  # Create file path in the script's directory
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

# Function to send a TCP packet to the specified IP and port
def send_packet_tcp(ip, port, packet):
    try:
        send(IP(dst=ip)/TCP(dport=port)/packet)
    except Exception as e:
        print(f"Failed to send TCP packet: {e}")

# Function to send a UDP packet to the specified IP and port
def send_packet_udp(ip, port, packet):
    try:
        send(IP(dst=ip)/UDP(dport=port)/packet)
    except Exception as e:
        print(f"Failed to send UDP packet: {e}")

# Function to create a 1MB file and send it in chunks over TCP
def send_file_tcp(ip, port):
    filename = 'file.txt'
    try:
        with open(filename, 'wb') as f:
            f.write(os.urandom(1024*1024))  # Generate 1MB random file
        with open(filename, 'rb') as f:
            packet = f.read(1024)
            while packet:
                send_packet_tcp(ip, port, packet)
                packet = f.read(1024)
        os.remove(filename)
    except Exception as e:
        print(f"Failed to send TCP file: {e}")

# Function to create a 1MB file and send it in chunks over UDP
def send_file_udp(ip, port):
    filename = 'file.txt'
    try:
        with open(filename, 'wb') as f:
            f.write(os.urandom(1024*1024))  # Generate 1MB random file
        with open(filename, 'rb') as f:
            packet = f.read(1024)
            while packet:
                send_packet_udp(ip, port, packet)
                packet = f.read(1024)
        os.remove(filename)
    except Exception as e:
        print(f"Failed to send UDP file: {e}")

# Thread function for TCP operations: send a packet, send a file, and log bandwidth
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

# Thread function for UDP operations: send a packet, send a file, and log bandwidth
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

# Main function to start TCP and UDP threads and wait for them to finish
def main():
    tcp = threading.Thread(target=tcp_thread)
    udp = threading.Thread(target=udp_thread)
    
    tcp.start()
    udp.start()
    
    tcp.join()
    udp.join()

if __name__ == '__main__':
    main()
