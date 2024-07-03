import socket

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

