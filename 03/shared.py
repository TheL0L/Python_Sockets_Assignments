import socket, struct

# ANSI escape codes
class ANSI:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'

# shared constants
_LOCALHOST = '127.0.0.1'
_PORTS = [30000, 30001, 30002, 30003, 30004]
_HEADER_FORMAT = '!BBHH'
_HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)

# shared methods
def port_select(ports: list) -> int:
    def port_input() -> int:
        print('Select a port:')
        for p in range(len(ports)):
            print(f'{p}. {ports[p]}')
        try:
            x = int(input())
        except:
            return -1
        return x if 0 <= x < len(ports) else -1

    port_index = port_input()
    while port_index == -1:
        LOG_ERROR('Selected port is invalid or taken.\n')
        port_index = port_input()
    return port_index

def LOG_MESSAGE(message: str) -> None:
    print(f'{ANSI.YELLOW}LOG: {message}{ANSI.RESET}')

def LOG_ERROR(message: str) -> None:
    print(f'{ANSI.RED}ERROR: {message}{ANSI.RESET}')

def attempt_handshake(ip: str, port: int) -> socket.socket:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect((ip, port))
        return sock
    except OSError as err:
        LOG_ERROR(f'connection to {ip}:{port} failed.\n\t{err}')  # log failed connections
        return None

# protocol methods
def request_servers(server_sock: socket.socket) -> None:
    # prepare header values
    _type       = 0
    _sub_type   = 0
    _len        = 0
    _sub_len    = 0

    # construct header
    bytes_header = struct.pack(_HEADER_FORMAT, _type, _sub_type, _len, _sub_len)

    # send header
    server_sock.send(bytes_header)
    return

def request_clients(server_sock: socket.socket) -> None:
    # prepare header values
    _type       = 0
    _sub_type   = 1
    _len        = 0
    _sub_len    = 0

    # construct header
    bytes_header = struct.pack(_HEADER_FORMAT, _type, _sub_type, _len, _sub_len)

    # send header
    server_sock.send(bytes_header)
    return

def send_servers(server_sock: socket.socket, data: str) -> None:
    # prepare data segment
    bytes_data  = data.encode()

    # prepare header values
    _type       = 1
    _sub_type   = 0
    _len        = len(bytes_data)
    _sub_len    = 0

    # construct header
    bytes_header = struct.pack(_HEADER_FORMAT, _type, _sub_type, _len, _sub_len)

    # send header & data
    server_sock.send(bytes_header)
    server_sock.send(bytes_data)
    return

def send_clients(server_sock: socket.socket, data: str) -> None:
    # prepare data segment
    bytes_data  = data.encode()

    # prepare header values
    _type       = 1
    _sub_type   = 1
    _len        = len(bytes_data)
    _sub_len    = 0

    # construct header
    bytes_header = struct.pack(_HEADER_FORMAT, _type, _sub_type, _len, _sub_len)

    # send header & data
    server_sock.send(bytes_header)
    server_sock.send(bytes_data)
    return

def set_username(server_sock: socket.socket, data: str) -> None:
    # prepare data segment
    bytes_username   = data.encode()
    sender_is_clinet = len(bytes_username) > 0

    # prepare header values
    _type       = 2
    _sub_type   = 1 if sender_is_clinet else 0
    _len        = len(bytes_username)
    _sub_len    = 0

    # construct header
    bytes_header = struct.pack(_HEADER_FORMAT, _type, _sub_type, _len, _sub_len)

    # send header & data
    server_sock.send(bytes_header)
    if sender_is_clinet:
        server_sock.send(bytes_username)
    return

def send_message(server_sock: socket.socket, sender: str, recipient: str, data: str) -> None:
    # prepare data segment
    bytes_recipient = recipient.encode()
    message         = f'{sender}\0{recipient}\0{data}'
    bytes_message   = message.encode()

    # prepare header values
    _type       = 3
    _sub_type   = 0
    _len        = len(bytes_message)
    _sub_len    = len(bytes_recipient)

    # construct header
    bytes_header = struct.pack(_HEADER_FORMAT, _type, _sub_type, _len, _sub_len)

    # send header & data
    server_sock.send(bytes_header)
    server_sock.send(bytes_message)
    return

