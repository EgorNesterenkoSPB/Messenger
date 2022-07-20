from pyfiglet import figlet_format
import getpass
import socket
import json
import atexit
import time
from termcolor import colored
import threading
from _thread import *
import ConstantStrings
import hashlib
import rsa
import pickle
from cryptography.fernet import Fernet


# def receiveMessageFromBuddy():

#     while True:
#         serverResponse = s.recv(1024)
#         serverResponse = f.decrypt(serverResponse).decode('utf8')
#         print(serverResponse)


def logout(userName):
    setOffineData = {ConstantStrings.actionKey:ConstantStrings.requestSetOnline,ConstantStrings.nameKey:userName,ConstantStrings.onlineKey:0} # to set 0 in db when application is closed and the user is offline
    jsonUserData = json.dumps(setOffineData)
    global f
    s.sendall(f.encrypt(jsonUserData.encode('utf8')))

def mainInterface(currentUserName):
    print(colored("-------Main page-------","magenta"))

    print(colored("User %s is successfully logged" % (currentUserName),"yellow"))
    print(colored(allCommandsString,"cyan"))

    while True:
        userCommand = input(">>")

        if userCommand == logoutString:
            logout(currentUserName)
            login()
            break
        elif userCommand == helpString:
            print(colored(allCommandsString,"cyan"))
        elif userCommand == backString:
            print(colored("You cant come back to previous stage, write /logout to finish this session","red"))
        elif userCommand == "/info":
            userData = {ConstantStrings.actionKey:ConstantStrings.requestUserInfo,ConstantStrings.nameKey:currentUserName}
            jsonUserData = json.dumps(userData)
            global f
            s.sendall(f.encrypt(jsonUserData.encode('utf8')))
            serverResponse = s.recv(1024)
            serverResponse = f.decrypt(serverResponse).decode('utf8')
            print(serverResponse)
        elif userCommand == "/online":
            userData = {ConstantStrings.actionKey:ConstantStrings.requestOnlineUsers}
            jsonUserData = json.dumps(userData)

            s.sendall(f.encrypt(jsonUserData.encode('utf8')))
            serverResponse = s.recv(1024)
            serverResponse = f.decrypt(serverResponse).decode('utf8')
            print("Online users:\n%s"%(serverResponse))
        elif userCommand == "/search":
            print(colored("-------Searching user-------","magenta"))
            print(colored("\nip - search user by ip\nname - search user by name","cyan"))

            while True:
                userData = ""
                searchChoosingUserBy = input(">>")

                if searchChoosingUserBy == logoutString:
                    logout(currentUserName)
                    login()
                    break
                if searchChoosingUserBy == helpString:
                    print(colored(allCommandsString,"cyan"))
                    continue
                if searchChoosingUserBy == backString:
                    print(colored("-------Back to main page-------","magenta"))
                    break
                if searchChoosingUserBy == "ip" or searchChoosingUserBy == "IP" or searchChoosingUserBy == "Ip":
                    searchIP = input("IP:")

                    if searchIP == logoutString:
                        logout(currentUserName)
                        login()
                        break
                    if searchIP == helpString:
                        print(colored(allCommandsString,"cyan"))
                        continue
                    if searchIP == backString:
                        print(colored("-------Back to choosing method to search user-------","magenta"))
                        break

                    userData = {ConstantStrings.actionKey:ConstantStrings.requestSearchUserTerminal,ConstantStrings.ipKey:searchIP}
                if searchChoosingUserBy == "name" or searchChoosingUserBy == "Name":
                    searchName = input(">>Name:")

                    if searchName == logoutString:
                        logout(currentUserName)
                        login()
                        break
                    if searchName == helpString:
                        print(colored(allCommandsString,"cyan"))
                        continue
                    if searchName == backString:
                        print(colored("-------Back to choosing method to search user-------","magenta"))
                        break
                else:
                    print(colored(unknownCommandString,"red"))
                    continue

                userData = {ConstantStrings.actionKey:ConstantStrings.requestSearchUserTerminal,ConstantStrings.nameKey:searchName}

                jsonUserData = json.dumps(userData)

                s.sendall(f.encrypt(jsonUserData.encode('utf8')))
                serverResponse = s.recv(1024)
                serverResponse = f.decrypt(serverResponse).decode('utf8')
                print(serverResponse)
        elif userCommand == "/chat":
            print(colored("-------Chat-------","magenta"))
            while True:
                chatBuddyName = input(">>Name:")

                if chatBuddyName == logoutString:
                    logout(currentUserName)
                    login()
                    break
                if chatBuddyName == helpString:
                    print(colored(allCommandsString,"cyan"))
                    continue
                if chatBuddyName == backString:
                    print(colored("-------Back to main page-------","magenta"))
                    break
                if chatBuddyName == currentUserName:
                    print(colored("You cant open chat with yourself","red"))
                    continue

                userData = {ConstantStrings.actionKey:ConstantStrings.requestChatConnect,ConstantStrings.nameKey:currentUserName,ConstantStrings.chatBuddyNameKey:chatBuddyName}
                jsonUserData = json.dumps(userData)

                s.sendall(f.encrypt(jsonUserData.encode('utf8')))
                serverResponse = s.recv(1024)
                serverResponse = f.decrypt(serverResponse).decode('utf8')
                print(serverResponse)
                serverResponseArray = serverResponse.split('\n')


                if serverResponseArray[0] == "Successful connection":
                    print(colored("Use /file:'filename' to send file\n/open:'filename' to open file\n/update to update chat","cyan"))

                    # receive_thread = threading.Thread(target=receiveMessageFromBuddy)
                    # receive_thread.start()

                    while True:
                        message = input(">>")
                        #message = ""
                        #writeMessage_thread = threading.Thread(target=sendMessage,args=(message,))
                        #writeMessage_thread.start()
                        #print("Test message %s" % (message))

                        if message == logoutString:
                            logout(currentUserName)
                            login()
                            break
                        if message == helpString:
                            print(colored(allCommandsString,"cyan"))
                            continue
                        if message == backString:
                            print(colored("-------Back to writing user name for connection chat stage-------","magenta"))
                            break
                        if message == "/update":
                            userMessage = {ConstantStrings.actionKey:ConstantStrings.requestUpdateChat,ConstantStrings.nameKey:currentUserName,ConstantStrings.chatBuddyNameKey:chatBuddyName}
                            jsonUserData = json.dumps(userMessage)

                            s.sendall(f.encrypt(jsonUserData.encode('utf8')))
                            serverResponse = s.recv(1024)
                            serverResponse = f.decrypt(serverResponse).decode('utf8')
                            print(serverResponse)
                            continue
                        if "/file:" in message:
                            fileName = message.partition("/file:")[2]

                            text_read = ""

                            try:
                                with open(fileName, "rb") as file_object:
                                    text_read = file_object.read()
                                    text_read = text_read.decode('utf8')
                            except:
                                print(colored("File with this name not found","red"))
                                continue

                            userMessage = {ConstantStrings.actionKey:ConstantStrings.requestSendFile,ConstantStrings.senderKey:currentUserName,ConstantStrings.receiverKey:chatBuddyName,ConstantStrings.dataKey:time.ctime(),ConstantStrings.fileNameKey:fileName,ConstantStrings.textKey:text_read}
                            jsonUserData = json.dumps(userMessage)


                            s.sendall(f.encrypt(jsonUserData.encode('utf8')))
                            continue
                        if "/open:" in message:
                            try:
                                fileName = message.partition("/open:")[2]
                            except:
                                print(colored("File with this name not found","red"))
                                continue
                            userMessage = {ConstantStrings.actionKey:ConstantStrings.requestOpenFile,ConstantStrings.fileNameKey:fileName}
                            jsonUserData = json.dumps(userMessage)


                            s.sendall(f.encrypt(jsonUserData.encode('utf8')))
                            serverResponse = s.recv(1024)
                            serverResponse = f.decrypt(serverResponse).decode('utf8')
                            print(serverResponse)
                            continue


                        userMessage = {ConstantStrings.actionKey:ConstantStrings.requestSendMessage,ConstantStrings.senderKey:currentUserName,ConstantStrings.receiverKey:chatBuddyName,ConstantStrings.dataKey:time.ctime(),ConstantStrings.messageKey:message}
                        jsonUserData = json.dumps(userMessage)

                        s.sendall(f.encrypt(jsonUserData.encode('utf8')))
                        # serverResponse = s.recv(1024)
                        # serverResponse = f.decrypt(serverResponse).decode('utf8')



                        #if serverResponse == "Message was send":
                        #    print("                                     %s(%s):%s\n" % (currentUserName,time.ctime(),message)[::-1])
                        #else:
                        #    print(serverResponse)


        else:
            print(colored(unknownCommandString,"red"))

def login():
    print(colored("-------Login-------","magenta"))

    while True:
        nameLogin = input(">>Name:")
        password = getpass.getpass('>>Password:')

        ip = "127.0.0.1"
        port = "8888"
        #ipInput = input("IP:")
        #portInput = input("Port:")

        if nameLogin == helpString or password == helpString:
            print(colored(allCommandsString,"cyan"))
        elif nameLogin == backString or password == backString:
            print(colored("-------Back to start page-------","magenta"))
            main()

        global f

        userData = {ConstantStrings.actionKey:ConstantStrings.loginAction,ConstantStrings.nameKey:nameLogin,ConstantStrings.passwordKey:password,ConstantStrings.ipKey:ip,ConstantStrings.portKey:port}
        jsonUserData = json.dumps(userData)
        s.sendall(f.encrypt(jsonUserData.encode('utf8')))
        serverResponse = s.recv(1024)
        serverResponse = f.decrypt(serverResponse).decode('utf8')
        print(serverResponse)

        if serverResponse == ConstantStrings.successLoginServerAnswer:
            global name
            name = nameLogin
            atexit.register(onExitApp,name) # to set online 0 when application was exited
            mainInterface(nameLogin)
            break

        elif serverResponse == ConstantStrings.failureLoginServerAnswer:
            print(colored("Name or password is wrong","red"))


def register():
    print(colored("-------Register-------","magenta"))

    while True:
        name = input(">>Name:")
        password = getpass.getpass('>>Password:')

        if name == helpString or password == helpString:
            print(colored(allCommandsString,"cyan"))
        elif name == backString or password == backString:
            print(colored("-------Back to start page-------","magenta"))
            main()
            break

        userData = {ConstantStrings.actionKey:ConstantStrings.registerAction,ConstantStrings.nameKey:name,ConstantStrings.passwordKey:password}
        jsonUserData = json.dumps(userData)

        global f
        s.sendall(f.encrypt(jsonUserData.encode('utf8')))
        serverResponse = s.recv(1024)
        serverResponse = f.decrypt(serverResponse).decode('utf8')
        print(serverResponse)

        if serverResponse == ConstantStrings.successRegisterServerAnswer:
            login()
            break
        elif serverResponse == ConstantStrings.failureRegisterServerAnswer:
            print(colored("This name is busy, use another one","red"))

def onExitApp(userName):
    print(colored("-------Exiting-------","magenta"))
    logout(userName)


def main():
    print(colored(figlet_format("Messenger"),"magenta"))
    print(colored("------------------------------------------------------------------\nMessenger - python TCP chat script using socket server,all data stores at SQLite\nAt first u need to start SocketServer.py and then at another terminal start mainTerminal.py file how many like u wanna create clients,it depends of you,but socket server limit is 10 clients,however u can rewrite it in code at anytime\nAll communication between server and client encrypted by RSA\nIf u prefer GUI,after launch socket server, start welcomePage.py file\nUse /help to show all commands\n------------------------------------------------------------------","white"))
    print("1-Login\n2-Register")

    while True:
        userLoginRegisterInput = input(">>")

        if userLoginRegisterInput == "1":
            login()
            break
        elif userLoginRegisterInput == "2":
            register()
            break
        elif userLoginRegisterInput == helpString:
            print(colored(allCommandsString,"cyan"))
        else:
            print("Write only 1 or 2")


if __name__ == '__main__':

    #//TODO: Global variables
    name = "no name"
    allCommandsString = "/logout - logout this session (you can use this command anywhere)\n/info - show my info (you can use this command anywhere)\n/online - show all users who are online\n/search - search users by name or ip\n/chat - start chat with user\n/back - step back to the previous stage (you can use this command anywhere)"
    helpString = "/help"
    logoutString = "/logout"
    backString = "/back"
    unknownCommandString = "Unknown command, use /help to see all available commands"

    print(colored("Genereting asymmetric key...","yellow"))

    # generate asymmetric key
    asyKey = rsa.newkeys(2048)
    publicKey = asyKey[0]
    privateKay = asyKey[1]

    s = socket.socket()
    try:
        s.connect(('',8888))
    except socket.error as error:
        print("Socket connection error:%s" %(str(error)))


    # Pass the public key to the server, and the sha256
    sendKey = pickle.dumps(publicKey)
    sendKeySha256 = hashlib.sha256(sendKey).hexdigest()
    s.sendall(pickle.dumps((sendKey,sendKeySha256)))

    # Accept the key passed by the server and decrypt it
    symKey,symKeySha256 = pickle.loads(s.recv(1024))

    if hashlib.sha256(symKey).hexdigest() != symKeySha256:
        print(colored("Client hash and server arent equeal, response from client","red"))
    else:
        symKey = pickle.loads(rsa.decrypt(symKey,privateKay))

        # Initialize the encrypted object
        f = Fernet(symKey)

        print(colored("Generation was successfuly end","yellow"))

        write_thread = threading.Thread(target=main)
        write_thread.start()
        #main()
