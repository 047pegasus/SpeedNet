#Python code to create a UDP server that listens on a specific port and sends a response to the client.

import socket

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

while True:
    print('\nwaiting to receive message')
    data, address = sock.recvfrom(8080)
    
    print('received {} bytes from {}'.format(len(data), address))
    print(data)
    
    if data:
        sent = sock.sendto(data, address)
        print('sent {} bytes back to {}'.format(sent, address))