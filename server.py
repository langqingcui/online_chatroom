import socket
import threading

PORT = 5000
SERVER = "0.0.0.0"
ADDRESS = (SERVER, PORT)
FORMAT = "gbk"

clients, names = [], []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def startChat():
    print("server is working on " + SERVER)
    server.listen()

    while True:
        try:
            conn, addr = server.accept()
            conn.send("NAME".encode(FORMAT))
            name = conn.recv(1024).decode(FORMAT)
            names.append(name)
            clients.append(conn)

            print(f"Name is :{name}")
            broadcastMessage(f"{name} has joined the chat!".encode(FORMAT))
            broadcastUserList()

            conn.send('Connection successful!'.encode(FORMAT))

            thread = threading.Thread(target=handle, args=(conn, addr))
            thread.start()
            print(f"active connections {threading.activeCount() - 2}")
        except Exception as e:
            print("Server stopped.")
            break

def handle(conn, addr):
    print(f"new connection {addr}")
    connected = True

    while connected:
        try:
            message = conn.recv(1024)
            broadcastMessage(message)
        except:
            connected = False

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
    while True:
        cmd = input()
        if cmd.lower() == "exit":
            print("Shutting down server...")
            for client in clients:
                client.close()
            server.close()
            break

startChat()
