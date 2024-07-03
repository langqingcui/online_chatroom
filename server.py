import socket
import threading
import sys

PORT = 5000
SERVER = "0.0.0.0"
ADDRESS = (SERVER, PORT)
FORMAT = "gbk"

clients, names = [], []
running = True  # Global flag to control server shutdown

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def startChat():
    global running
    print("Server is working on " + SERVER)
    server.listen()

    while running:
        try:
            conn, addr = server.accept()
            conn.send("NAME".encode(FORMAT))
            name = conn.recv(1024).decode(FORMAT)
            names.append(name)
            clients.append(conn)

            print(f"Name is :{name}")
            broadcastMessage(f"{name} has joined the chat!".encode(FORMAT))
            broadcastUserList()

            # Start a new thread to handle this connection
            thread = threading.Thread(target=handle, args=(conn, addr))
            thread.start()
            print(f"Active connections {threading.activeCount() - 2}")
            
            if not running:
                break
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Server stopped due to: {e}")
            break

def handle(conn, addr):
    global running
    print(f"New connection {addr}")
    connected = True

    while connected and running:
        try:
            message = conn.recv(1024)
            if not message:
                break
            broadcastMessage(message)
        except:
            break

    names.remove(getClientName(conn))
    clients.remove(conn)
    broadcastUserList()
    conn.close()

def broadcastMessage(message):
    for client in clients:
        client.send(message)

def broadcastUserList():
    user_list_message = "USER_LIST:" + ",".join(names)
    for client in clients:
        client.send(user_list_message.encode(FORMAT))

def getClientName(client):
    index = clients.index(client)
    return names[index]

def control_server():
    global running
    while True:
        cmd = input()
        if cmd.lower() == "exit":
            print("Shutting down server...")
            running = False
            for client in clients:
                client.close()
            server.close()

# Start the control server thread
control_thread = threading.Thread(target=control_server, daemon=True)
control_thread.start()

# Start the chat server
startChat()
