## Python code to create a TCP server that listens on a specific port and sends a message to the client when a connection is established.
import socket

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_address = ('localhost', 10000)
print('Starting up on {} port {}'.format(*server_address))
server.bind(server_address)

# Listen for incoming connections
server.listen(1)

while True:
    # Wait for a connection
    print('Waiting for a connection...')
    connection, client_address = server.accept()
    try:
        print('Connection from', client_address)

        # Send data
        message = b'Hello, World!'
        connection.sendall(message)
    finally:
        # Clean up the connection
        connection.close()