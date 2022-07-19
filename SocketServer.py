import socket 
import json
import sqlite3
import os
from _thread import *
import threading
import ConstantStrings
import hashlib
import rsa
import pickle
from cryptography.fernet import Fernet
from termcolor import colored


connectionsSymmetricKeys = {}
#clients = set()


def Padding(s):
    return s + ((16 - len(s) % 16) * '`')

#//TODO: Create and socket server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_Inet - use ethernet socket, SOCK_STREAM - use TCP protocol
try:
    s.bind(('127.0.0.1',8888)) 
except socket.error as error:
    print(str(error))

s.listen(10)

#//TODO: Set up client and get data

def threaded_client(connection):
    jsonUserData = '' # for convert data from client to json

    #//TODO: Create database

    conn = sqlite3.connect(ConstantStrings.databaseUserName)
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS chat(
        Sender TEXT,
        Receiver TEXT,
        data TEXT,
        message TEXT);
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        name TEXT,
        password TEXT,
        ip TEXT,
        port TEXT,
        online INT,
        connection TEXT); 
        """)
    cur.close()
    conn.commit()
    conn.close()


    def fetchAllChats():
        conn = sqlite3.connect(ConstantStrings.databaseUserName)
        cur = conn.cursor()

        cur.execute("SELECT * FROM chat;")
        results = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()

        return results

    def fetchAllUsers():
        conn = sqlite3.connect(ConstantStrings.databaseUserName)
        cur = conn.cursor()

        cur.execute("SELECT * FROM users;")
        results = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()

        return results

    while True:
        data = connection.recv(2048)
        print("before decrypt %s" %(data))

        currentSymmetricKey = connectionsSymmetricKeys[connection]



        data = currentSymmetricKey.decrypt(data).decode('utf8')

        print("ater decrypt %s" %(data))
        jsonUserData += data
        userData = json.loads(jsonUserData)
        print(userData)


        if userData[ConstantStrings.actionKey] == ConstantStrings.registerAction:  # register user
            users = fetchAllUsers()

            if len(users) == 0:
                conn = sqlite3.connect(ConstantStrings.databaseUserName)
                cur = conn.cursor()

                cur.execute("""INSERT INTO users(name,password,online) VALUES ('%s','%s','%s');""" % (userData[ConstantStrings.nameKey],userData[ConstantStrings.passwordKey],0))
                cur.close()
                conn.commit()
                conn.close()

                connection.sendall(currentSymmetricKey.encrypt(ConstantStrings.successRegisterServerAnswer.encode('utf8'))) # to send bytes
            else:
                for user in users:
                    if user[0] == userData[ConstantStrings.nameKey]:
                        connection.sendall(currentSymmetricKey.encrypt(ConstantStrings.failureRegisterServerAnswer.encode('utf8')))
                        break
                    else:
                        conn = sqlite3.connect(ConstantStrings.databaseUserName)
                        cur = conn.cursor()

                        cur.execute("""INSERT INTO users(name,password,online) VALUES ('%s','%s','%s');""" % (userData[ConstantStrings.nameKey],userData[ConstantStrings.passwordKey],0))
                        cur.close()
                        conn.commit()
                        conn.close()
                        connection.sendall(currentSymmetricKey.encrypt(ConstantStrings.successRegisterServerAnswer.encode('utf8')))
                        break
                        

        if userData[ConstantStrings.actionKey] == ConstantStrings.loginAction: # login user

            # conn = sqlite3.connect(ConstantStrings.databaseUserName)
            # cur = conn.cursor()
            # cur.execute('''UPDATE users SET currentSymmetricKey = ? WHERE name = ?''', (str(currentSymmetricKey), userData[ConstantStrings.nameKey]))
            # cur.close()
            # conn.commit()
            # conn.close()

            results = fetchAllUsers()
            if len(results) != 0:
                for user in results:
                    if user[0] == userData[ConstantStrings.nameKey] and user[1] == userData[ConstantStrings.passwordKey]:
                        connection.sendall(currentSymmetricKey.encrypt(ConstantStrings.successLoginServerAnswer.encode('utf8')))

                        conn = sqlite3.connect(ConstantStrings.databaseUserName)
                        cur = conn.cursor()
                        cur.execute('''UPDATE users SET online = ? WHERE name = ?''', (1, userData[ConstantStrings.nameKey]))
                        cur.execute('''UPDATE users SET ip = ? WHERE name = ?''', (userData[ConstantStrings.ipKey], userData[ConstantStrings.nameKey]))
                        cur.execute('''UPDATE users SET port = ? WHERE name = ?''', (userData[ConstantStrings.portKey], userData[ConstantStrings.nameKey]))
                        cur.execute('''UPDATE users SET connection = ? WHERE name = ?''', (str(connection), userData[ConstantStrings.nameKey]))
                        cur.execute('''UPDATE users SET connection = ? WHERE name = ?''', (0, userData[ConstantStrings.nameKey]))
                        cur.close()
                        conn.commit()
                        conn.close()


                        break
                    else:
                        if user == results[len(results)-1]:
                            connection.sendall(currentSymmetricKey.encrypt(ConstantStrings.failureLoginServerAnswer.encode('utf8')))
            else:
                connection.sendall(currentSymmetricKey.encrypt(ConstantStrings.failureLoginServerAnswer.encode('utf8')))
        
        if userData[ConstantStrings.actionKey] == ConstantStrings.requestOnlineUsers:
            results = fetchAllUsers()
            usersName = ""
            for user in results:
                if user[4] == 1:
                    usersName += "%s\n" % user[0]
            connection.sendall(currentSymmetricKey.encrypt(usersName.encode('utf8')))

        if userData[ConstantStrings.actionKey] == ConstantStrings.requestSetOnline:
            
            if userData[ConstantStrings.onlineKey] == 1:
                conn = sqlite3.connect(ConstantStrings.databaseUserName)
                cur = conn.cursor()
                cur.execute('''UPDATE users SET online = ? WHERE name = ?''', (1, userData[ConstantStrings.nameKey]))
                cur.close()
                conn.commit()
                conn.close()
            else:
                conn = sqlite3.connect(ConstantStrings.databaseUserName)
                cur = conn.cursor()
                cur.execute('''UPDATE users SET online = ? WHERE name = ?''', (0, userData[ConstantStrings.nameKey]))
                cur.close()
                conn.commit()
                conn.close()
        
        if userData[ConstantStrings.actionKey] == ConstantStrings.requestSearchUser:
            result = fetchAllUsers()
            userInfo = ""

            if ConstantStrings.nameKey in userData and userData.get(ConstantStrings.ipKey) is None:
                for user in result:
                    if user[0] == userData[ConstantStrings.nameKey]:
                        userInfo = "Online: %s,Port: %s,IP: %s,Name: %s" % (user[4],user[3],user[2],user[0])
                        connection.sendall(currentSymmetricKey.encrypt(userInfo.encode('utf8')))
                        break
                    else:
                        if user == result[len(result)-1]:
                            connection.sendall(currentSymmetricKey.encrypt("No user with this name".encode('utf8')))

            elif ConstantStrings.ipKey in userData and userData.get(ConstantStrings.nameKey) is None:
                for user in result:
                    if user[2] == userData[ConstantStrings.ipKey]:
                        userInfo = "Online: %s,Port: %s,IP: %s,Name: %s" % (user[4],user[3],user[2],user[0])
                        connection.sendall(currentSymmetricKey.encrypt(userInfo.encode('utf8')))
                        break
                    else:
                        if user == result[len(result)-1]:
                            connection.sendall(currentSymmetricKey.encrypt("User with this ip not found".encode('utf8')))
            elif ConstantStrings.nameKey in userData and ConstantStrings.ipKey in userData:
                for user in result:
                    if user[0] == userData[ConstantStrings.nameKey] and user[2] == userData[ConstantStrings.ipKey]:
                        userInfo = "Online: %s,Port: %s,IP: %s,Name: %s" % (user[4],user[3],user[2],user[0])
                        connection.sendall(currentSymmetricKey.encrypt(userInfo.encode('utf8')))
                        break
                    else:
                        if user == result[len(result)-1]:
                            connection.sendall(currentSymmetricKey.encrypt(ConstantStrings.failureSearchUserServerAnswer.encode('utf8')))
            else:
                connection.sendall(currentSymmetricKey.encrypt(ConstantStrings.failureSearchUserServerAnswer.encode('utf8')))

        #//TODO: Console command handle

        if userData[ConstantStrings.actionKey] == ConstantStrings.requestUserInfo: # console command from client
            result = fetchAllUsers()
            userInfo = ""

            for user in result:
                if userData[ConstantStrings.nameKey] == user[0]:
                    userInfo = "Name: %s\nIP: %s\nPort: %s\nOnline: %s" % (user[0],user[2],user[3],user[4])
                    connection.sendall(currentSymmetricKey.encrypt(userInfo.encode('utf8')))
                    break
        if userData[ConstantStrings.actionKey] == ConstantStrings.requestSearchUserTerminal:
            result = fetchAllUsers()
            userInfo = ""
            if ConstantStrings.nameKey in userData and userData.get(ConstantStrings.ipKey) is None:
                for user in result:
                        if user[0] == userData[ConstantStrings.nameKey]:
                            userInfo = "-------------\nName: %s\nIP: %s\nPort: %s\nOnline: %s" % (user[0],user[2],user[3],user[4])
                            connection.sendall(currentSymmetricKey.encrypt(userInfo.encode('utf8')))
                            break
                        else:
                            if user == result[len(result)-1]:
                                connection.sendall(currentSymmetricKey.encrypt("No user with this name".encode('utf8')))
            elif ConstantStrings.ipKey in userData and userData.get(ConstantStrings.nameKey) is None:
                for user in result:
                        if user[2] == userData[ConstantStrings.ipKey]:
                            userInfo = "-------------\nName: %s\nIP: %s\nPort: %s\nOnline: %s" % (user[0],user[2],user[3],user[4])
                            connection.sendall(currentSymmetricKey.encrypt(userInfo.encode('utf8')))
                            break
                        else:
                            if user == result[len(result)-1]:
                                connection.sendall(currentSymmetricKey.encrypt("No user with this ip".encode('utf8')))

            
        if userData[ConstantStrings.actionKey] == ConstantStrings.requestChatConnect:
            result = fetchAllUsers()
            chats = fetchAllChats()
            currentChat = ""

            for user in result:
                if user[0] == userData[ConstantStrings.chatBuddyNameKey]:
                    if user[4] == 1: # check if online the user
                        for chat in chats:
                            if chat[0] == userData[ConstantStrings.nameKey]:
                                currentChat += "                                                           %s(%s):%s\n" % (chat[0],chat[2],chat[3])[::-1]
                            elif chat[1] == userData[ConstantStrings.nameKey]:
                                currentChat += "%s(%s):%s\n" % (chat[0],chat[2],chat[3])
                        sendData = "Successful connection\n%s" % (currentChat)
                        connection.sendall(currentSymmetricKey.encrypt(sendData.encode('utf8')))
                        break
                    else:
                        connection.sendall(currentSymmetricKey.encrypt("User isnt online".encode('utf8')))
                        break
                else:
                    if user == result[len(result)-1]:
                        connection.sendall(currentSymmetricKey.encrypt("User with this name not found".encode('utf8')))
        
        if userData[ConstantStrings.actionKey] == ConstantStrings.requestUpdateChat:
            chats = fetchAllChats()
            currentChat = ""

            for chat in chats:
                if chat[0] == userData[ConstantStrings.nameKey]:
                    currentChat += "                                                           %s(%s):%s\n" % (chat[0],chat[2],chat[3])[::-1]
                elif chat[1] == userData[ConstantStrings.nameKey]:
                    currentChat += "%s(%s):%s\n" % (chat[0],chat[2],chat[3])
            connection.sendall(currentSymmetricKey.encrypt(currentChat.encode('utf8')))
            
            

        if userData[ConstantStrings.actionKey] == ConstantStrings.requestSendMessage:
            
            try:
                conn = sqlite3.connect(ConstantStrings.databaseUserName)
                cur = conn.cursor()
                cur.execute("""INSERT INTO chat(Sender,Receiver,data,message) VALUES ('%s','%s','%s','%s');""" % (userData[ConstantStrings.senderKey],userData[ConstantStrings.receiverKey],userData[ConstantStrings.dataKey],userData[ConstantStrings.messageKey]))
                cur.close()
                conn.commit()
                conn.close()
                #connection.sendall(currentSymmetricKey.encrypt("Chat was changed\n".encode('utf8')))
                print("Message was send")
            except:
                #connection.sendall(currentSymmetricKey.encrypt("Error sending message".encode('utf8')))
                print("Error sending message")
            
            users = fetchAllUsers()

            # for user in users:
            #     if user[0] == userData["Receiver"]:
            #         for client in clients:
            #             if str(client) == user[5]:
            #                 client.sendall(connectionsSymmetricKeys[client].encrypt(userData[ConstantStrings.messageKey].encode('utf8')))


        if userData[ConstantStrings.actionKey] == ConstantStrings.requestSendFile:
            filename = os.path.basename(userData[ConstantStrings.fileNameKey]) # remove path if there is
            text = ""

            with open("Server_%s" % (filename),"wb") as file:
                text = userData[ConstantStrings.textKey]
                text = text.encode('utf8')
                if not text:
                    break
                
                file.write(text)

                conn = sqlite3.connect(ConstantStrings.databaseUserName)
                cur = conn.cursor()
                cur.execute("""INSERT INTO chat(Sender,Receiver,data,message) VALUES ('%s','%s','%s','Sent file:%s');""" % (userData[ConstantStrings.senderKey],userData[ConstantStrings.receiverKey],userData[ConstantStrings.dataKey],filename))
                cur.close()
                conn.commit()
                conn.close()
                connection.sendall(currentSymmetricKey.encrypt("Upload chat\n".encode('utf8')))
        if  userData[ConstantStrings.actionKey] == ConstantStrings.requestOpenFile:
            filename = userData[ConstantStrings.fileNameKey]
            text = ""

            with open("Server_%s" % (filename),"rb") as file:
                text = file.read()
            connection.sendall(currentSymmetricKey.encrypt(text))

            #chats = fetchAllChats()

            #lastMessage = chats[len(chats)-1]

            #if lastMessage[0] == userData["Sender"]:

        jsonUserData = ''

        if not data:
            break

    connection.close()


while True:
    connection,addr = s.accept()

    # Accept the public key passed by the client
    publicKeyPK, pubKeySha256 = pickle.loads(connection.recv(1024))
    if hashlib.sha256(publicKeyPK).hexdigest() != pubKeySha256:
        print(colored("Hash client and server arent equal,response from server","red"))
    else:
        publicKey = pickle.loads(publicKeyPK)
        print("Accepted public key")
    
    #encrypting and passing a symmetric key with a public key.
    #Generate a key for symmetric encryption
    symKey = Fernet.generate_key()
    encryptedSymKey = rsa.encrypt(pickle.dumps(symKey),publicKey)
    encryptedSymKeySha256 = hashlib.sha256(encryptedSymKey).hexdigest()

    connection.sendall(pickle.dumps((encryptedSymKey,encryptedSymKeySha256)))

    # Initialize the encrypted object
    f = Fernet(symKey)

    #store current session user symmetric key 
    connectionsSymmetricKeys[connection] = f



    #clients.add(connection)
    start_new_thread(threaded_client,(connection,))
s.close()



