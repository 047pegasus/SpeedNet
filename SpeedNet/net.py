import socket
import time
import os

# Check the operating system
if os.name != 'nt':  # 'nt' means Windows
    import fcntl
else:
    import msvcrt

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
            if os.name != 'nt':  # Unix-like system
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(data)
                fcntl.flock(f, fcntl.LOCK_UN)
            else:  # Windows system
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1024)
                f.write(data)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1024)

# Function to generate a small file of size 1MB and send it to the given IP address using sockets
def send_file(ip, port):
    filename = 'file.txt'
    with open(filename, 'wb') as f:
        f.write(os.urandom(1024 * 1024))
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
    # Calculate bandwidth in MB/s
    bandwidth = len(packet) / (end - start) / 1024 / 1024
    data = f'Bandwidth: {bandwidth:.2f} MB/s\n'
    write_to_file(data)

    start = time.time()
    send_file(ip, port)
    end = time.time()
    # Calculate bandwidth in MB/s
    bandwidth = 1 / (end - start)
    data = f'Bandwidth: {bandwidth:.2f} MB/s\n'
    write_to_file(data)

if __name__ == '__main__':
    main()
