import socket, threading

def port_select(PORTS : list) -> int:
    print('Select a port:')
    for p in range(len(PORTS)):
        print(f'{p}. {PORTS[p]}')
    x = int(input())
    return x if 0 <= x < len(PORTS) else -1

def setup_listener(port : int) -> socket:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('0.0.0.0', port))
    listener.listen(1)
    return listener

def await_connections(listener : socket) -> None:
    LOG('awaiting for connections...')
    while True:
        conn, client_address = listener.accept()
        LOG(f'connection with {client_address} established.')
        threading.Thread(target=respond_to_client, args=(conn, client_address)).start()

def attempt_handshake(ip : str, port : int) -> socket:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect((ip, port))
        return sock
    except OSError as err:
        LOG(f'connection to {ip}:{port} failed.\n\t{err}')  # log failed connections
        return None

def respond_to_client(conn_socket : socket, client_address : tuple[str, int]) -> None:
    try:
        data = conn_socket.recv(_PACKET_SIZE)
        message = data.decode()
        print(f'{client_address} -> me: {message}')
        if message.lower() == 'hello':
            message = b'World'
            conn_socket.send(message)
            print(f'me -> {client_address}: {message}')
    except OSError as err:
        LOG(f'an error occurred while responding to client.\n\t{err}')

def initiate_dialog(conn_socket : socket, client_address : tuple[str, int]) -> None:
    try:
        message = b'Hello'
        conn_socket.send(message)
        print(f'me -> {client_address}: {message}')
        data = conn_socket.recv(_PACKET_SIZE)
        message = data.decode()
        print(f'{client_address} -> me: {message}')
        if message.lower() == 'world':
            print('dialog finished.')
            return
        else:
            print('bad response.')
    except OSError as err:
        LOG(f'an error occurred while holding a conversation.\n\t{err}')

def LOG(message : str) -> None:
    print(f'LOG: {message}')


# constants
_LOCALHOST = '127.0.0.1'
_PACKET_SIZE = 1024

# (hopefully) constant list of ports
_PORTS = [30000, 30001, 30002, 30003, 30004]

# port selection
port_index = port_select(_PORTS)
while port_index == -1:
    LOG('ERROR: Selected port is invalid or taken.\n')
    port_index = port_select(_PORTS)

# handshake attempts with everyone, except ourselves
connections = {(_LOCALHOST, p):attempt_handshake(_LOCALHOST, p) for p in _PORTS if p != _PORTS[port_index]}

# discard any failed connections
connections = {addr:c for addr,c in connections.items() if c is not None}

# send messages over successful connections
threads = []
for addr, c in connections.items():
    x = threading.Thread(target=initiate_dialog, args=(c, addr))
    threads.append(x)
    x.start()

# listener setup
listener = setup_listener(_PORTS[port_index])
await_connections(listener)

# unreachable code due to endless listener
# adding a timeout to the listener will solve it

# close all connections
LOG('closing all connections...')
listener.close()
for _, c in connections:
    c.close()

LOG('done.')

