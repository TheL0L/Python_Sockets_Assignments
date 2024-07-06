import socket, sys, threading, time
import shared

def await_messages(server_sock: socket.socket):
    while True:
        response = shared.receive_via_socket(server_sock)

        # if caught any errors
        if response['error'] is not None:
            # check if it was caused due to the connection closing
            if isinstance(response['error'], ConnectionResetError):
                # close the socket, and end the thread
                server_sock.close()
                shared.LOG_MESSAGE('connection with server has been closed.')
                return
            # otherwise continue
            continue
        
        # ignore any protocol messages that aren't direct messages
        if response['type'] != 3:
            continue

        # unpack message
        sender, recipient, message = response['data'].split('\0', 2)
        print(f'{sender} -> {recipient}: {message}')

def measure_rtt(server_sock: socket.socket) -> float:
    if server_sock is None:
        return -1
    
    # start measuring rtt
    rtt = time.time()

    # send ping and wait for a reply
    shared.send_ping(server_sock)
    response = shared.receive_via_socket(server_sock)

    # end measuring rtt
    rtt = time.time() - rtt

    # check for any errors
    if response['error'] is not None:
        return -1
    
    # check for reply validity
    if response['type'] != 4 or response['sub_type'] != 1:
        return -1
    
    return rtt


RTTs = {}

# measure rtt for each server
for port in shared._PORTS:
    server_sock = shared.attempt_handshake(shared._LOCALHOST, port)
    if server_sock is None:
        RTTs[port] = -1
        continue
    RTTs[port] = measure_rtt(server_sock)
    server_sock.close()

# discard failed ports
RTTs = {port: rtt for port, rtt in RTTs.items() if rtt >= 0}

if len(RTTs) == 0:
    shared.LOG_MESSAGE('Could not connect to any server, closing client...')
    input('press any key to exit.')
    exit()

# connect to the server with the lowest rtt
server_sock = shared.attempt_handshake(shared._LOCALHOST, min(RTTs, key=RTTs.get))
if server_sock is None:
    shared.LOG_MESSAGE('Closing client...')
    input('press any key to exit.')
    exit()

# send username to the server
username = input('Enter your name: ')
shared.set_username(server_sock, username, True)

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
