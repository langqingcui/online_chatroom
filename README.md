# online_chatroom

## ssh到华为云服务器
```bash
ssh root@120.46.87.122
```
password: Online_chatroom

## 更新server.py
如果需要更新server.py，你需要首先ssh到云服务器。然后，本地终端进入存放server.py的目录，输入以下命令：
```bash
scp ./server.py root@120.46.87.122:~
```