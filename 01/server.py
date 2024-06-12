import socket

USERS = {}

def find_user(address):
    for user, addr in USERS.items():
        if addr == address:
            return user
    return f'{addr[0]}:{addr[1]}'


def LOG(message):
    print(f'LOG: {message}')

UDP_IP = '0.0.0.0'
UDP_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.bind((UDP_IP, UDP_PORT))

LOG(f'listener socket created at {UDP_IP}:{UDP_PORT}')

while True:
    # UTF-8 byte stream, tuple(ip, port)
    data, addr = sock.recvfrom(1024)
    plaintext = data.decode()

    if plaintext.find(' ') == -1:
        if plaintext not in USERS:
            USERS[plaintext] = addr
            LOG(f'{plaintext} has logged in!')
    else:
        recipient, message = plaintext.split(' ', 1)
        sender = find_user(addr)

        if recipient in USERS:
            modified_data = f'{sender}: {message}'
            sock.sendto(modified_data.encode(), USERS[recipient])
            LOG(f'{sender} -> {recipient}: {message}')
        else:
            modified_data = f'ERROR! user "{sender}" has not logged in yet! message discarded!'
            sock.sendto(modified_data.encode(), addr)
            LOG(f'{sender} -> {recipient}: {message}')

    