import socket
import threading
import base64
import os
from tkinter import filedialog
from tkinter import *
from tkinter import font
from tkinter import ttk
from PIL import Image, ImageTk

PORT = 5000
SERVER = "172.20.10.3"  # 请根据您的实际情况修改服务器IP
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

# Create a new client socket
# and connect to the server
client = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)
client.connect(ADDRESS)

# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self):

        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.Window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # login window
        self.login = Toplevel()
        self.login.protocol("WM_DELETE_WINDOW", self.on_closing)
        # set the title
        self.login.title("Login")
        self.login.resizable(width=False,
                             height=False)
        self.login.configure(width=400,
                             height=300)
        # create a Label
        self.pls = Label(self.login,
                         text="Please login to continue",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text="Name: ",
                               font="Helvetica 12")

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.2)

        # create a entry box for typing the message
        self.entryName = Entry(self.login,
                               font="Helvetica 14")

        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)

        # set the focus of the cursor
        self.entryName.focus()

        # create a Continue Button along with action
        self.go = Button(self.login,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.goAhead(self.entryName.get()))

        self.go.place(relx=0.4,
                      rely=0.55)
        self.Window.mainloop()

    def on_closing(self):
        client.close()
        self.Window.destroy()
        exit(0)

    def goAhead(self, name):
        self.login.destroy()
        self.layout(name)

        # the thread to receive messages
        rcv = threading.Thread(target=self.receive)
        rcv.start()

        # add protocol to close the window and exit
        self.Window.protocol("WM_DELETE_WINDOW", self.on_closing)

    # The main layout of the chat
    def layout(self, name):
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=700,
                              height=550,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text=self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=700,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.7,
                            relwidth=0.7,
                            rely=0.08)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.825)

        # Create a frame for the buttons
        self.buttonFrame = Frame(self.Window, bg="#ABB2B9")
        self.buttonFrame.place(relwidth=1,
                               relheight=0.05,
                               rely=0.775)

        # Add buttons to the frame
        self.btnImage = Button(self.buttonFrame,
                               text="Image",
                               font="Helvetica 10 bold",
                               bg="#2C3E50",
                               fg="#EAECEE",
                               command=self.sendImage)
        self.btnImage.pack(side=LEFT, padx=5)

        self.btnEmoji = Button(self.buttonFrame,
                               text="Emoji",
                               font="Helvetica 10 bold",
                               bg="#2C3E50",
                               fg="#EAECEE",
                               command=self.sendEmoji)
        self.btnEmoji.pack(side=LEFT, padx=5)

        self.btnSendFile = Button(self.buttonFrame,
                                  text="Send File",
                                  font="Helvetica 10 bold",
                                  bg="#2C3E50",
                                  fg="#EAECEE",
                                  command=self.sendFile)
        self.btnSendFile.pack(side=LEFT, padx=5)  # 添加到按钮框架中

        self.entryMsg = Entry(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")

        # place the given widget into the gui window
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)

        self.entryMsg.focus()

        # bind the return key to send message
        self.entryMsg.bind("<Return>", lambda event: self.sendButton(self.entryMsg.get()))

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get()))

        self.buttonMsg.place(relx=0.77,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

        # create a label to display the number of online users
        self.userOnlineLabel = Label(self.Window,
                                     bg="#17202A",
                                     fg="#EAECEE",
                                     font="Helvetica 12",
                                     text="User Online: 0")  # Default text with 0 online users
        self.userOnlineLabel.place(relwidth=0.3,
                                   relheight=0.05,
                                   rely=0.08,
                                   relx=0.70)

        # create a listbox to display online users
        self.onlineUsers = Listbox(self.Window,
                                   bg="#17202A",
                                   fg="#EAECEE",
                                   font="Helvetica 12")
        self.onlineUsers.place(relwidth=0.3,
                               relheight=0.64,
                               rely=0.13,
                               relx=0.70)

    def sendImage(self):
        pass

    def sendFile(self):
        file_path = filedialog.askopenfilename(title="Select a file to send")
        if file_path:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                file_name = os.path.basename(file_path)
                # 将文件数据编码为 Base64
                base64_file_data = base64.b64encode(file_data).decode('utf-8')
                file_size = len(base64_file_data)
                # 发送文件元数据和 Base64 编码的文件数据
                message = f"FILE:{file_name}:{file_size}".encode(FORMAT)
                client.send(message)
                # 发送 Base64 文件数据
                chunk_size = 1024  # 定义每个数据块的大小
                for i in range(0, len(base64_file_data), chunk_size):
                    chunk = base64_file_data[i:i + chunk_size]
                    client.send(chunk.encode(FORMAT))  # 发送 Base64 数据块

                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, f"File '{file_name}' sent successfully.\n")
                self.textCons.config(state=DISABLED)

    def sendEmoji(self):
        # Implement the logic to handle sending emojis
        pass

    # function to start the thread for sending messages
    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        snd = threading.Thread(target=self.sendMessage)
        snd.start()

    # function to receive messages
    def receive(self):
        buffer = ""
        while True:
            try:
                buffer += client.recv(1024).decode(FORMAT)
                while "/n" in buffer:
                    # if the messages from the server is NAME send the client's name
                    message, buffer = buffer.split("/n", 1)
                    if message == 'NAME':
                        client.send(self.name.encode(FORMAT))
                    elif message.startswith('USER_LIST:'):
                        # update the online users list
                        users = message.split(':')[1].split(',')
                        self.onlineUsers.delete(0, END)
                        for user in users:
                            self.onlineUsers.insert(END, user)
                        user_count = len(users)
                        self.userOnlineLabel.config(text=f"User Online: {user_count}")
                    elif message.startswith('FILE:'):
                        # 处理文件传输请求
                        print(message)
                        filename, filesize_str = message[5:].split(':')
                        filesize = int(filesize_str)
                        base64_file_data = ""
                        received_size = 0
                        while received_size < filesize:
                            data = client.recv(1024).decode(FORMAT)
                            base64_file_data += data
                            received_size += len(data)
                        # 将 Base64 文件数据解码为二进制数据
                        file_data = base64.b64decode(base64_file_data)
                        save_path = os.path.join('.', 'text', filename)  # 定义文件保存路径为当前目录下的 'text' 文件夹

                        # 确保保存目录存在
                        if not os.path.exists(os.path.dirname(save_path)):
                            os.makedirs(os.path.dirname(save_path))

                        # 初始化文件接收状态
                        with open(save_path, 'wb') as file:
                            try:
                                file.write(file_data)
                            except Exception as e:
                                print(e)
                                print("Error writing file data")
                                client.close()
                                break

                            # 保存完成后，更新 GUI
                            self.textCons.config(state=NORMAL)
                            self.textCons.insert(END, f"File {filename} received and saved to {save_path}\n")
                            self.textCons.config(state=DISABLED)
                    else:
                        # insert messages to text box
                        self.textCons.config(state=NORMAL)
                        self.textCons.insert(END, message + "\n\n")

                        self.textCons.config(state=DISABLED)
                        self.textCons.see(END)
            except Exception as e:
                # an error will be printed on the command line or console if there's an error
                print(e)
                client.close()
                break

    # function to send messages
    def sendMessage(self):
        self.textCons.config(state=DISABLED)
        while True:
            message = (f"{self.name}: {self.msg}")
            client.send(message.encode(FORMAT))
            break


# create a GUI class object
g = GUI()
