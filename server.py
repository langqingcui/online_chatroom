import socket
import threading
import sys

PORT = 5000
SERVER = "0.0.0.0"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

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
            conn.send("NAME/n".encode(FORMAT))
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
            message = conn.recv(1024).decode(FORMAT)
            if not message:
                break
            if message.startswith('FILE:'):
                print("file message " + message)
                # 处理文件传输请求
                filename, filesize = message[5:].split(':')
                filesize = int(filesize)
                broadcastMessage(f"FILE:{filename}:{filesize}/n".encode(FORMAT), exclude_conn=conn)
                print(f"Received file transfer request for {filename} of size {filesize} bytes")
                # 接收文件数据
                for i in range(filesize // 1024 + 1):
                    data = conn.recv(1024)
                    print("Send file data", i, "data:", data[:10])
                    # 广播文件传输请求，除了发送者
                    broadcastFile(data, exclude_conn=conn)
            else:
                print("normal message " + message)
                # 正常消息处理
                broadcastMessage(message.encode(FORMAT))
        except:
            connected = False

    names.remove(getClientName(conn))
    clients.remove(conn)
    broadcastUserList()
    conn.close()

def broadcastMessage(message, exclude_conn=None):
    for client in clients:
        if client != exclude_conn:
            client.send(message + b'/n')

def broadcastFile(message, exclude_conn=None):
    for client in clients:
        if client != exclude_conn:
            client.send(message)
            
def broadcastUserList():
    user_list_message = "USER_LIST:" + ",".join(names) + '/n'
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
