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
    print("-------Main page-------")

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
            print("-------Searching user-------")
            print("\nip - search user by ip\nname - search user by name")

            while True:
                userData = ""
                searchChoosingUserBy = input(">>")

                if searchChoosingUserBy == logoutString:
                    logout(currentUserName)
                    login()
                    break
                if searchChoosingUserBy == helpString:
                    print(allCommandsString)
                    continue
                if searchChoosingUserBy == backString:
                    print("-------Back to main page-------")
                    break
                if searchChoosingUserBy == "ip" or searchChoosingUserBy == "IP" or searchChoosingUserBy == "Ip":
                    searchIP = input("IP:")

                    if searchIP == logoutString:
                        logout(currentUserName)
                        login()
                        break
                    if searchIP == helpString:
                        print(allCommandsString)
                        continue
                    if searchIP == backString:
                        print("-------Back to choosing method to search user-------")
                        break

                    userData = {"action":"Request:search user terminal","ip":searchIP}
                if searchChoosingUserBy == "name" or searchChoosingUserBy == "Name":
                    searchName = input(">>Name:")

                    if searchName == logoutString:
                        logout(currentUserName)
                        login()
                        break
                    if searchName == helpString:
                        print(allCommandsString)
                        continue
                    if searchName == backString:
                        print("-------Back to choosing method to search user-------")
                        break

                    userData = {"action":"Request:search user terminal","name":searchName}

                jsonUserData = json.dumps(userData).encode('utf8')
                s.sendall(jsonUserData)
                serverResponse = s.recv(1024).decode('utf8')
                print(serverResponse)
        elif userCommand == "/chat":
            print("-------Chat-------")
            while True:
                chatBuddyName = input(">>Name:")

                if chatBuddyName == logoutString:
                    logout(currentUserName)
                    login()
                    break
                if chatBuddyName == helpString:
                    print(allCommandsString)
                    continue
                if chatBuddyName == backString:
                    print("-------Back to main page-------")
                    break

                userData = {"action":"Request:chat connect","name":currentUserName,"chatBuddyName":chatBuddyName}
                jsonUserData = json.dumps(userData).encode('utf8')
                s.sendall(jsonUserData)
                serverResponse = s.recv(1024).decode('utf8')
                print(serverResponse)

                if serverResponse == "Successful connecion":
                    print("Use /file to send file")
                    while True:
                        message = input(">>")

                        if message == logoutString:
                            logout(currentUserName)
                            login()
                            break
                        if message == helpString:
                            print(allCommandsString)
                            continue
                        if message == backString:
                            print("-------Back to writing user name for connection chat stage-------")
                            break




        
        else:
            print(unknownCommandString)

def login():
    print("-------Login-------")

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
            print("-------Back to start page-------")
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
    print("-------Register-------")

    while True:
        name = input(">>Name:")
        password = getpass.getpass('>>Password:')

        if name == helpString or password == helpString:
            print(allCommandsString)
        elif name == backString or password == backString:
            print("-------Back to start page-------")
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
    print("-------Exiting-------")
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
    allCommandsString = "/logout - logout this session (you can use this command anywhere)\n/info - show my info (you can use this command anywhere)\n/online - show all users who are online\n/search - search users by name or ip\n/chat - start chat with user\n/back - step back to the previous stage (you can use this command anywhere)"
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