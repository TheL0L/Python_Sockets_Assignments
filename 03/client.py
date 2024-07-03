import socket, struct, sys, threading
import shared

def await_messages(server_sock: socket.socket):
    while True:
        # receive header bytes
        try:
            bytes_header = server_sock.recv(shared._HEADER_SIZE)
            _type, _sub_type, _len, _sub_len = struct.unpack(bytes_header)
        except OSError as err:
            shared.LOG_ERROR(f'an error occurred while retrieving message header.\n\t{err}')
            continue

        # receive data bytes
        try:
            bytes_data = server_sock.recv(_len)
            data       = bytes_data.decode()
        except OSError as err:
            shared.LOG_ERROR(f'an error occurred while retrieving message data.\n\t{err}')
            continue
        
        # ignore any protocol messages that aren't direct messages
        if _type != 3:
            continue

        # unpack message
        sender, recipient, message = data.split('\0', 2)
        print(f'{sender} -> {recipient}: {message}')

# port selection
port_index = shared.port_select(shared._PORTS)

# handshake attempt with selected server
server_sock = shared.attempt_handshake(shared._LOCALHOST, shared._PORTS[port_index])
if server_sock is None:
    shared.LOG_MESSAGE('Closing client...')
    input('press any key to exit.')
    exit()

# send username to the server
username = input('Enter your name: ')
shared.set_username(server_sock, username)

# create listener for the server
server_listener = threading.Thread(target=await_messages, args=(server_sock,))
server_listener.start()

# get user input and send via server
for line in sys.stdin:
    recipient, message = line.strip().split(' ', 1)
    shared.send_message(server_sock, username, recipient, message)

# close connection with server
server_sock.close()
server_listener.join()

shared.LOG_MESSAGE('done.')
