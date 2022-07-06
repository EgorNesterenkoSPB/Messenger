from cmath import pi
from pyfiglet import figlet_format
import getpass
import socket
import threading
import json
import atexit

def logout(userName):
    setOffineData = {"action":"set online","name":userName,"online":0} # to set 0 in db when application is closed and the user is offline
    jsonUserData = json.dumps(setOffineData).encode('utf8')
    s.sendall(jsonUserData)

def mainInterface(currentUserName):

    print("User %s is successfully logged" % (currentUserName))
    print(allCommandsString)

    while True:
        userCommand = input(">>")

        if userCommand == logoutString:
            logout(currentUserName)
            login()
            break
        elif userCommand == helpString:
            print(allCommandsString)
        elif userCommand == backString:
            print("You cant come back to previous stage, write /logout to finish this session")
        elif userCommand == "/info":
            userData = {"action":"Request:userInfo","name":currentUserName}
            jsonUserData = json.dumps(userData).encode('utf8')
            s.sendall(jsonUserData)
            serverResponse = s.recv(1024).decode('utf8')
            print(serverResponse)
        elif userCommand == "/online":
            userData = {"action":"Request:online users"}
            jsonUserData = json.dumps(userData).encode('utf8')
            s.sendall(jsonUserData)
            serverResponse = s.recv(1024).decode('utf8')
            print("Online users:\n%s"%(serverResponse))
        elif userCommand == "/search":
            searchName = input("Name:")
            userData = {"action":"Request:search user terminal","name":searchName}
            jsonUserData = json.dumps(userData).encode('utf8')
            s.sendall(jsonUserData)
            serverResponse = s.recv(1024).decode('utf8')
            print(serverResponse)

        
        else:
            print(unknownCommandString)

def login():

    while True:
        nameLogin = input(">>Name:")
        password = getpass.getpass('>>Password:')

        ip = "127.0.0.1"
        port = "8888"
        #ipInput = input("IP:")
        #portInput = input("Port:")

        if nameLogin == helpString or password == helpString:
            print(allCommandsString)
        elif nameLogin == backString or password == backString:
            main()

        userData = {"action":"login","name":nameLogin,"password":password,"ip":ip,"port":port}
        jsonUserData = json.dumps(userData).encode('utf8')
        s.sendall(jsonUserData)
        serverResponse = s.recv(1024).decode('utf8')
        print(serverResponse)

        if serverResponse == "Success login":
            global name
            name = nameLogin
            atexit.register(onExitApp,name) # to set online 0 when application was exited
            mainInterface(nameLogin)
            break

        elif serverResponse == "Error login":
            print("Name or password is wrong")


def register():

    while True:
        name = input(">>Name:")
        password = getpass.getpass('>>Password:')

        if name == helpString or password == helpString:
            print(allCommandsString)
        elif name == backString or password == backString:
            main()
            break

        userData = {"action":"register","name":name,"password":password}
        jsonUserData = json.dumps(userData).encode('utf8')
        s.sendall(jsonUserData)
        serverResponse = s.recv(1024).decode('utf8')
        print(serverResponse)

        if serverResponse == "Success register":
            login()
            break
        elif serverResponse == "Error register":
            print("This name is busy, use another one")

def onExitApp(userName):
    print("Exiting")
    logout(userName)


def main():
    print(figlet_format("Messenger"))
    print("Use /help to show all commands\n")
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
            print(allCommandsString)
        else:
            print("Write only 1 or 2")




if __name__ == '__main__':

    #//TODO: Global variables
    name = "no name"
    allCommandsString = "/logout - logout this session\n/info - show my info\n/online - show all users who are online\n/search - search users by name or ip\n/chat - start chat with user\n/back - step back to the previous stage"
    helpString = "/help"
    logoutString = "/logout"
    backString = "/back"
    unknownCommandString = "Unknown command, use /help to see all available commands"

    s = socket.socket()
    try:
        s.connect(('',8888))
    except socket.error as error:
        print("Socket connection error:%s" %(str(error)))

    main()