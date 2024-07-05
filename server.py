import socket
import threading
import sys
import sqlite3
import time

PORT = 5000
SERVER = "0.0.0.0"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

clients = []
user_dict = {}  # key: username, value: name
running = True  # Global flag to control server shutdown

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

# create user database
db_conn = sqlite3.connect('chatapp.db', check_same_thread=False)
cursor = db_conn.cursor()

#refresh the data base
#cursor.execute("DROP TABLE IF EXISTS users")
#cursor.execute("DROP TABLE IF EXISTS friends")

cursor.execute('''CREATE TABLE IF NOT EXISTS users
             (
              name TEXT NOT NULL,
              username TEXT PRIMARY KEY NOT NULL,
              password TEXT NOT NULL
              )''')
db_conn.commit()

# 创建私聊记录数据库
cursor.execute('''CREATE TABLE IF NOT EXISTS private_messages
             (
              sender TEXT NOT NULL,
              receiver TEXT NOT NULL,
              message TEXT NOT NULL,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
              )''')
db_conn.commit()

# create friend database
cursor.execute('''CREATE TABLE IF NOT EXISTS friends
             (
              user1 TEXT NOT NULL,
              user2 TEXT NOT NULL,
              PRIMARY KEY (user1, user2)
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
            elif message.startswith("LOAD_CHAT_HISTORY"):
                handle_load_chat_history(conn, message)
            elif message.startswith("PRIVATE"):
                handle_private_message(conn, message)
            elif message.startswith("SEARCH"):
                handle_search(conn, message)
            elif message.startswith("FRIEND_LIST"):
                handle_friend_list(conn, message)
            elif message.startswith('FILE:'):
                print("file message " + message)
                # 处理文件传输请求
                filename, filesize = message[5:].split(':')
                filesize = int(filesize)
                broadcastFileMessage(f"FILE:{filename}:{filesize}/n".encode(FORMAT), exclude_conn=conn)
                print(f"Received file transfer request for {filename} of size {filesize} bytes")
                # 接收文件数据
                for i in range(filesize // 1024 + 1):
                    data = conn.recv(1024)
                    print("Send file data", i, "data:", data[:10])
                    # 广播文件传输请求，除了发送者
                    broadcastFile(data, exclude_conn=conn)
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
        username = getClientUsername(conn)
        if username:
            del user_dict[username]
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
        user_dict[username] = name
        # 发送好友列表
        friend_list_message = create_friend_list_message(username)
        conn.send(friend_list_message.encode(FORMAT))
        broadcastUserList()
        broadcastMessage(f"{name} has joined the chat!".encode(FORMAT))  
    else:
        conn.send("Login failed".encode(FORMAT))

def handle_load_chat_history(conn, message):
    sender, receiver = message.split(":")[1], message.split(":")[2]
    cursor.execute("SELECT sender, message FROM private_messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY timestamp", (sender, receiver, receiver, sender))
    messages = cursor.fetchall()
    for msg in messages:
        chat_message = f"LOAD_CHAT_HISTORY:{sender}:{receiver}:{msg[0]}:{msg[1]}/n"
        conn.send(chat_message.encode(FORMAT))

def handle_private_message(conn, message):
    sender, receiver, message = message.split(":")[1], message.split(":")[2], message.split(":")[3]
    cursor.execute("INSERT INTO private_messages (sender, receiver, message) VALUES (?,?,?)", (sender, receiver, message))
    db_conn.commit()
    for client in clients:
        if getClientUsername(client) == receiver:
            client.send(f"PRIVATE:{sender}:{receiver}:{message}/n".encode(FORMAT))
            break

# 搜索处理
def handle_search(conn, message):
    my_username, search_username = message.split(":")[1], message.split(":")[2]
    cursor.execute("SELECT * FROM users WHERE username=?", (search_username,))
    if cursor.fetchone():
        # 检查是否已经是好友
        cursor.execute("SELECT * FROM friends WHERE user1=? AND user2=? OR user1=? AND user2=?", 
                       (my_username, search_username, search_username, my_username))
        if cursor.fetchone():
            conn.send("Already friends".encode(FORMAT) + b"/n")
        else:
            # 添加好友关系
            cursor.execute("INSERT INTO friends (user1, user2) VALUES (?, ?)", (my_username, search_username))
            db_conn.commit()
            conn.send(f"found successfully".encode(FORMAT) + b"/n")
            
            # 更新双方的好友列表
            for client in clients:
                username = getClientUsername(client)
                if username == my_username or username == search_username:
                    friend_list_message = create_friend_list_message(username)
                    client.send(friend_list_message.encode(FORMAT))
            # 强制刷新在线用户列表，保证加好友之后能直接在好友列表中显示在线
            broadcastUserList()
    else:
        conn.send("User not found".encode(FORMAT) + b"/n")

# 处理好友列表请求
def handle_friend_list(conn, message):
    my_username = message.split(":")[1]
    friend_list_message = create_friend_list_message(my_username)
    conn.send(friend_list_message.encode(FORMAT))

def broadcastMessage(message):
    for client in clients:
        client.send(message+b"/n")

def broadcastFile(data, exclude_conn):
    for client in clients:
        if client != exclude_conn:
            client.send(data)
            
def broadcastFileMessage(message, exclude_conn):
    for client in clients:
        if client != exclude_conn:
            client.send(message+b'/n')

def broadcastUserList():
    user_list_message = "USER_LIST:" + ",".join([f"{username}/{name}" for username, name in user_dict.items()]) + "/n"
    for client in clients:
        client.send(user_list_message.encode(FORMAT))

def create_friend_list_message(username):
    cursor.execute("SELECT user1, user2 FROM friends WHERE user1=? OR user2=?", (username, username))
    friends = cursor.fetchall()
    friend_list = []
    for user1, user2 in friends:
        if user1 == username:
            friend_username = user2
        else:
            friend_username = user1
        
        # 获取朋友的姓名
        cursor.execute("SELECT name FROM users WHERE username=?", (friend_username,))
        friend_name = cursor.fetchone()[0]
        friend_list.append(f"{friend_name}({friend_username})")
    return "FRIEND_LIST:" + ",".join(friend_list) + "/n"

def getClientUsername(client):
    index = clients.index(client)
    return list(user_dict.keys())[index]

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
