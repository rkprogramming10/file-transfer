import socket
from threading import Thread
import time
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

BUFFER_SIZE = 4096
clients = {}
IP_ADDRESS = '127.0.0.1'
PORT = 5000
SERVER = None


def grantAccess(client_name):
    global clients
    other_client_name = clients[client_name]['connected_with']
    other_client_socket = clients[other_client_name]['client']
    message = 'Access granted'
    other_client_socket.send(message.encode())


def declineAccess(client_name):
    global clients
    other_client_name = clients[client_name]['connected_with']
    other_client_socket = clients[other_client_name]['client']
    message = f'Access declined by {client_name}'
    other_client_socket.send(message.encode())


def handleSendFile(client_name, file_name, fileSize):
    global clients
    clients[client_name]['file_name'] = file_name
    clients[client_name]['file_size'] = fileSize
    other_client_name = clients[client_name]['connected_with']
    other_client_socket = clients[other_client_name]['client']
    message = f'\n{client_name} want to send {file_name} file with the{fileSize}. Do you want to download? y/n'
    other_client_socket.send(message.encode())

    msg_down = f'downlaod: {file_name}'
    other_client_socket.send(msg_down.encode())


is_dir_accessed = os.path.isdir('shared_files')
if not is_dir_accessed:
    os.makedirs('shared_files')


def sendTextMessage(client_name, message):
    global clients
    other_client_name = clients[client_name]['connected_with']
    other_client_socket = clients[other_client_name]['client']
    final_message = client_name + '>' + message
    other_client_socket.send(final_message.encode())


def handleErrorMessage(client):
    message = '''
    you need to connect with one of the client first befor sending any message. click on referesh to see all availabe users'''
    client.send(message.encode())


def disconnectWithClient(message, client, client_name):
    global clients
    enter_client_name = message[11:].strip()

    if enter_client_name in clients:

        clients[enter_client_name]['connected_with'] = ''
        clients[client_name]['connected_with'] = ''

        other_client_socket = clients[enter_client_name]['client']

        greet_message = f'Hello, {enter_client_name} you are successfully disconnected with {client_name}'
        other_client_socket.send(greet_message.encode())

        msg = f'Your are successfully disconnected with a {enter_client_name}'
        client.send(msg.encode())


def connectWithClient(message, client, client_name):
    global clients
    enter_client_name = message[8:].strip()
    if enter_client_name in clients:
        if (not clients[client_name]['connected_with']):
            clients[enter_client_name]['connected_with'] = client_name
            clients[client_name]['connected_with'] = enter_client_name

            other_client_socket = clients[enter_client_name]['client']

            greet_message = f'Hello, {enter_client_name} {client_name}  connected with you'
            other_client_socket.send(greet_message.encode())

            msg = f'Your are successfully connected with {enter_client_name}'
            client.send(msg.encode())
        else:
            other_client_name = clients[client_name]['connected_with']
            msg = f'You are already connected with {other_client_name}'
            client.send(msg.encode())


def handleShowList(client):
    global clients
    counter = 0
    for c in clients:
        print
        counter += 1
        client_address = clients[c]['address'][0]
        connected_with = clients[c]['connected_with']
        message = ''
        if connected_with:
            message = f'{counter}, {c}, {client_address}, connected with {connected_with}, tiul,\n'
        else:
            message = f'{counter}, {c}, {client_address}, Availabe, tiul,\n'
        client.send(message.encode())
        time.sleep(1)


def handle_message(client, message, client_name):
    if message == 'show list':
        handleShowList(client)
    elif message[:7] == 'connect':
        connectWithClient(message, client, client_name)
    elif message[:10] == 'disconnect':
        disconnectWithClient(message, client, client_name)

    elif message == 'y' or message == 'yes':
        grantAccess(client_name)
    elif message == 'n' or message == 'no':
        declineAccess(client_name)

    else:
        connected = clients[client_name]['connected_with']
        if connected:
            sendTextMessage(client_name, message)
        else:
            handleErrorMessage(client)


def handle_client(client, client_name):
    global clients, BUFFER_SIZE, SERVER
    banner1 = 'Welcome you are connected to server\nClick on refresh to see all availabe Users\nSelect the user and click on connect to start chatting'
    client.send(banner1.encode())

    while True:
        try:
            BUFFER_SIZE = clients[client_name]['file_size']
            chunk = client.recv(BUFFER_SIZE)
            message = chunk.decode().strip().lower()
            if message:
                handle_message(client, message,  client_name)

        except:
            pass


def accept_connection():
    global SERVER, clients
    while True:
        client, addr = SERVER.accept()
        client_name = client.recv(4096).decode().lower()
        clients[client_name] = {
            'client': client,
            'address': addr,
            'connected_with': '',
            'file_name': '',
            'file_size': 4096,
        }
        print(f'Connection established with {client_name} : {addr}')
        thread = Thread(target=handle_client, args=(client, client_name))
        thread.start()


def setup():
    print('\n\t\t\t\tIP MESSENGER\n')
    global SERVER, PORT, IP_ADDRESS
    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind((IP_ADDRESS, PORT))
    SERVER.listen(100)
    print('\t\t\t\tServer is waiting for incoming connection\n')
    accept_connection()


def ftp():
    global IP_ADDRESS

    authorizer = DummyAuthorizer()
    authorizer.add_user('lftpd', 'lftpd', '.', perm='elradfmw')

    handler = FTPHandler
    handler.authorizer = authorizer

    ftp_server = FTPServer((IP_ADDRESS, 21), handler)
    ftp_server.serve_forever()


setup_thread = Thread(target=setup)
setup_thread.start()

ftp_thread = Thread(target=ftp)
ftp_thread.start()
