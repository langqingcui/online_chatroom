# import all the required modules
import socket
import threading
import base64
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
 
PORT = 5000
SERVER = "10.26.41.189"
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
        
        self.private_chats = {}
        self.message_queues = {}
        self.user_list = []
 
        # login window
        self.login = Toplevel()
        self.login.protocol("WM_DELETE_WINDOW", self.on_closing)
        # set the title
        self.login.title("Login")
        self.login.resizable(width=False,
                             height=False)
        self.login.configure(width=400,
                             height=400)
        # create a Label
        self.pls = Label(self.login,
                         text="Please login to continue",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)

        # 昵称输入
        self.labelName = Label(self.login, text="Name: ", font="Helvetica 12")
        self.labelName.place(relheight=0.1, relx=0.1, rely=0.25)
        self.entryName = Entry(self.login, font="Helvetica 14")
        self.entryName.place(relwidth=0.4, relheight=0.08, relx=0.35, rely=0.25)

        # 用户名输入
        self.labelUserName = Label(self.login, text="Username: ", font="Helvetica 12")
        self.labelUserName.place(relheight=0.1, relx=0.1, rely=0.35)
        self.entryUserName = Entry(self.login, font="Helvetica 14")
        self.entryUserName.place(relwidth=0.4, relheight=0.08, relx=0.35, rely=0.35)

        # 密码输入
        self.labelPass = Label(self.login, text="Password: ", font="Helvetica 12")
        self.labelPass.place(relheight=0.1, relx=0.1, rely=0.45)
        self.entryPass = Entry(self.login, font="Helvetica 14", show='*')
        self.entryPass.place(relwidth=0.4, relheight=0.08, relx=0.35, rely=0.45)

        #登录执行函数
        self.go = Button(self.login, text="LOGIN", font="Helvetica 14 bold", command=lambda: self.loginUser(self.entryName.get(),self.entryUserName.get(), self.entryPass.get()))
        self.go.place(relx=0.4, rely=0.6)

        #注册执行函数
        self.register = Button(self.login, text="REGISTER", font="Helvetica 14 bold", command=lambda: self.registerUser(self.entryName.get(),self.entryUserName.get(), self.entryPass.get()))
        self.register.place(relx=0.4, rely=0.8)
        self.Window.mainloop()
        
    def on_closing(self):
        client.close()
        self.Window.destroy()
        exit(0)
 
    
    
    def loginUser(self,name,username, password):
        self.username = username
        message = f"LOGIN:{name}:{username}:{password}"
        client.send(message.encode(FORMAT))
        response = client.recv(1024).decode(FORMAT)
        if response == "Login successful":
            self.login.destroy()
            self.layout(name, username)
            rcv = threading.Thread(target=self.receive)
            rcv.start()
        else:
            self.show_error("Login failed. Please try again.")

    def registerUser(self,name,username,password):
        message = f"REGISTER:{name}:{username}:{password}"
        client.send(message.encode(FORMAT))
        response = client.recv(1024).decode(FORMAT)
        if response == "Registration successful":
            self.show_info("Registration successful. You can now log in.")
        else:
            self.show_error("Registration failed. Username may already exist.")

    def show_error(self, message):
        error = Toplevel(self.login)
        error.title("Error")
        error.geometry("300x100")
        Label(error, text=message, font="Helvetica 12").pack(pady=10)
        Button(error, text="OK", command=error.destroy).pack()

    def show_info(self, message):
        info = Toplevel(self.login)
        info.title("Info")
        info.geometry("300x100")
        Label(info, text=message, font="Helvetica 12").pack(pady=10)
        Button(info, text="OK", command=info.destroy).pack()
 
    # The main layout of the chat
    def layout(self, name, username):
        self.name = name
        self.username = username
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False,
                            height=False)
        self.Window.configure(width=500,
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

        # Add the search entry
        self.searchEntry = Entry(self.buttonFrame,
                                 bg="#2C3E50",
                                 fg="#EAECEE",
                                 font="Helvetica 13")
        self.searchEntry.pack(side=LEFT, padx=5)

        # Add the search button
        self.searchButton = Button(self.buttonFrame,
                                   text="Add",
                                   font="Helvetica 10 bold",
                                   bg="#ABB2B9",
                                   command=self.searchUser)
        self.searchButton.pack(side=LEFT, padx=5)

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
                            relheight=0.31,
                            rely=0.13,
                            relx=0.70)
        
        #create a label to display all the friends
        self.myFriendLabel = Label(self.Window,
                                    bg="#17202A",
                                    fg="#EAECEE",
                                    font="Helvetica 12",
                                    text="my friend")  
        self.myFriendLabel.place(relwidth=0.3,
                                relheight=0.05,
                                rely=0.44,
                                relx=0.70)
        
        # create a listbox to display online users
        self.myFriend = Listbox(self.Window,
                                bg="#17202A",
                                fg="#EAECEE",
                                font="Helvetica 12")
        self.myFriend.place(relwidth=0.3,
                            relheight=0.28,
                            rely=0.49,
                            relx=0.70)
        

        # Bind double-click event to Listbox
        self.myFriend.bind("<Double-1>", self.open_private_chat)
        

    def searchUser(self):
        my_username = self.username
        search_username = self.searchEntry.get()
        message = f"SEARCH:{my_username}:{search_username}"
        client.send(message.encode(FORMAT)) 
        
    
    def open_private_chat(self, event):
        selected_index = self.myFriend.curselection()[0]
        selected_user = self.myFriend.get(selected_index)
        selected_username = selected_user.split('(')[1][:-1]
        selected_name = selected_user.split('(')[0]
        if selected_username == self.username:
            messagebox.showwarning("Private Chat Error", "You cannot begin a private chat with yourself.")
            return
        if selected_username not in self.private_chats:
            self.private_chats[selected_username] = PrivateChatWindow(self, selected_username, selected_name)
            self.private_chats[selected_username].window.lift()
            if selected_username in self.message_queues:
                for msg in self.message_queues[selected_username]:
                    self.private_chats[selected_username].receiveMessage(msg)
                del self.message_queues[selected_username]
        self.private_chats[selected_username].focus()


    def sendImage(self):
        pass

    def sendEmoji(self):
        pass
    
    # function to start the thread for sending messages
    def sendButton(self, msg):
        if msg.strip():  # Check if the message is not empty or just spaces
            self.textCons.config(state=DISABLED)
            self.msg = msg
            self.entryMsg.delete(0, END)
            snd = threading.Thread(target=self.sendMessage)
            snd.start()
        else:
            messagebox.showwarning("Warning", "Empty message cannot be sent")
 
    # function to receive messages
    def receive(self):
        buffer = ""
        while True:
            try:
                buffer += client.recv(1024).decode(FORMAT)
                while "/n" in buffer:
                    message, buffer = buffer.split("/n", 1)
                    if message.startswith("USER_LIST:"):
                        print("Received user list")
                        # update the online users list
                        try:
                            user_list = message.split(':')[1].split(',')
                            self.user_list = [(user.split('/')[0], user.split('/')[1]) for user in user_list if '/' in user]
                            self.onlineUsers.delete(0, END)
                            for user in self.user_list:
                                self.onlineUsers.insert(END, f"{user[1]}({user[0]})")
                            user_count = len(self.user_list)
                            self.userOnlineLabel.config(text=f"User Online: {user_count}")
                            # Update friend list with online status
                            for i in range(self.myFriend.size()):
                                friend = self.myFriend.get(i)
                                friend_username = friend.split('(')[1][:-1]
                                if any(user[0] == friend_username for user in self.user_list):
                                    self.myFriend.itemconfig(i, {'fg': 'white'})
                                else:
                                    self.myFriend.itemconfig(i, {'fg': 'gray'})
                        except IndexError:
                            print("Error parsing user list")
                    elif message.startswith("FRIEND_LIST:"):
                        print("Received friend list")
                        friends = message.split(':')[1].split(',')
                        self.myFriend.delete(0, END)
                        for friend in friends:
                            self.myFriend.insert(END, friend)
                    elif message == "User not found":
                        messagebox.showinfo("Info", "User not found")
                    elif message.startswith("found successfully"):
                        print("添加成功")
                        messagebox.showinfo("Info", f"User found and added to your friends list")
                    elif message.startswith("Already"):
                        messagebox.showinfo("Info", "Already friend")
                    
                    elif message.startswith('PRIVATE'):
                        print(message)
                        sender, receiver, msg = message.split(':')[1:]
                        if receiver == self.username:
                            if sender in self.private_chats:
                                self.private_chats[sender].receiveMessage(f"{sender}: {msg}")
                            else:
                                if sender not in self.message_queues:
                                    self.message_queues[sender] = []
                                self.message_queues[sender].append(f"{sender}: {msg}")

                    elif message.startswith("LOAD_CHAT_HISTORY:"):
                        parts = message.split(':', -1)
                        if len(parts) == 5:
                            sender, receiver, chat_history = parts[1], parts[2], parts[3] + ": " + parts[4]
                            if receiver == self.username and sender in self.private_chats:
                                for msg in chat_history.split("/n"):
                                    if msg:
                                        self.private_chats[sender].receiveMessage(msg)
                            elif sender == self.username and receiver in self.private_chats:
                                for msg in chat_history.split("/n"):
                                    if msg:
                                        self.private_chats[receiver].receiveMessage(msg)
                    else:
                        print("Received message")
                            # insert messages to text box
                        self.textCons.config(state=NORMAL)
                        self.textCons.insert(END, message+"\n\n")
                        self.textCons.config(state=DISABLED)
                        self.textCons.see(END)
                    
            except (ConnectionResetError, ConnectionAbortedError):
                print(self.name + " connection closed")
                client.close()
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                client.close()
                break
 
    # function to send messages
    def sendMessage(self):
        self.textCons.config(state=DISABLED)
        while True:
            message = (f"{self.name}: {self.msg}")
            client.send(message.encode(FORMAT))
            break
 
class PrivateChatWindow:
    def __init__(self, parent, username, name):
        self.parent = parent
        self.username = username
        self.name = name
        
        self.window = Toplevel()
        self.window.title(f"Private Chat with {name}")
        self.window.geometry("400x400")
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.textCons = Text(self.window, bg="#17202A", fg="#EAECEE", font="Helvetica 14", padx=5, pady=5)
        self.textCons.place(relheight=0.8, relwidth=1, relx=0, rely=0)
        self.textCons.config(state=DISABLED)

        self.entryMsg = Entry(self.window, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        self.entryMsg.place(relwidth=0.74, relheight=0.06, relx=0.011, rely=0.82)
        self.entryMsg.focus()
        self.entryMsg.bind("<Return>", lambda event: self.sendButton(self.entryMsg.get()))
        
        self.buttonMsg = Button(self.window, text="Send", font="Helvetica 10 bold", width=20, bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get()))
        self.buttonMsg.place(relx=0.77, rely=0.82, relheight=0.06, relwidth=0.22)

        self.msg_queue = []

        self.load_chat_history()

    def load_chat_history(self):
        client.send(f"LOAD_CHAT_HISTORY:{self.parent.username}:{self.username}".encode(FORMAT))

    def on_closing(self):
        if self.username in self.parent.private_chats:
            del self.parent.private_chats[self.username]
        self.window.destroy()

    def sendButton(self, msg):
        if msg.strip():
            self.textCons.config(state=DISABLED)
            self.msg = msg
            self.entryMsg.delete(0, END)
            snd = threading.Thread(target=self.sendMessage)
            snd.start()
        else:
            messagebox.showwarning("Warning", "Empty message cannot be sent")

    def sendMessage(self):
        message = f"PRIVATE:{self.parent.username}:{self.username}:{self.msg}/n"
        client.send(message.encode(FORMAT))
        self.receiveMessage(f"{self.parent.username}: {self.msg}")

    def receiveMessage(self, msg):
        print("private receive message")
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, msg + "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
    
    def focus(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()


 
# create a GUI class object
g = GUI()
