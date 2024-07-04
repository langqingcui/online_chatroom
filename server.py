import socket
import threading
import sys
import sqlite3
import time

PORT = 5000
SERVER = "0.0.0.0"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

clients, names = [], []
running = True  # Global flag to control server shutdown

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

# 创建用户数据库
db_conn = sqlite3.connect('chatapp.db', check_same_thread=False)
cursor = db_conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
             (
              name TEXT NOT NULL,
              username TEXT PRIMARY KEY NOT NULL,
              password TEXT NOT NULL
              )''')
db_conn.commit()

def startChat():
    global running
    print("Server is working on " + SERVER)
    server.listen()

    while running:
        try:
            conn, addr = server.accept()
            
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
            
            if message.startswith("REGISTER"):
                handle_register(conn, message)
            elif message.startswith("LOGIN"):
                handle_login(conn, message)
            else:
                broadcastMessage(message.encode(FORMAT))
        except ConnectionResetError:
            print(f"Connection reset by peer {addr}")
            connected = False
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    if conn in clients:
        names.remove(getClientName(conn))
        clients.remove(conn)
        broadcastUserList()
        conn.close()

# 注册处理
def handle_register(conn, message):
    name, username, password = message.split(":")[1], message.split(":")[2],message.split(":")[3]

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.send("Username already exists".encode(FORMAT))
    else:
        cursor.execute("INSERT INTO users (name, username, password) VALUES (?,?,?)", (name, username, password))
        db_conn.commit()
        conn.send("Registration successful".encode(FORMAT))

# 登录处理
def handle_login(conn, message):
    name, username, password = message.split(":")[1], message.split(":")[2],message.split(":")[3]
   
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    if cursor.fetchone():
        conn.send("Login successful".encode(FORMAT))
        clients.append(conn)
        names.append(name)
        broadcastUserList()
        broadcastMessage(f"{name} has joined the chat!".encode(FORMAT))  
    else:
        conn.send("Login failed".encode(FORMAT))

def broadcastMessage(message):
    for client in clients:
        client.send(message+b"/n")
        

def broadcastUserList():
    user_list_message = "USER_LIST:" + ",".join(names)  + "/n"
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
