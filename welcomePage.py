import tkinter as tk
from tkinter import messagebox
import socket
import json
import threading
import errorUIElement

#//TODO: Connect w/ socket server

s = socket.socket()

try:
    s.connect(('',8888))
except socket.error as error:
    print(str(error))

#//TODO: Views

class ApplicationRoot(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, LoginPage, RegisterPage,MainPage):


            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        loginButton = tk.Button(self, text="Login",
                            command=lambda: controller.show_frame(LoginPage))

        registerButton = tk.Button(self, text="Register",
                            command=lambda: controller.show_frame(RegisterPage))

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)

        loginButton.grid(row=0,column=0)
        registerButton.grid(row=1,column=0)
        


class LoginPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        backButton = tk.Button(self, text="Back",command=lambda: controller.show_frame(StartPage))
        backButton.grid(row=0, column=0, sticky="nw")

        entryUserName = tk.Entry(master=self)
        entryUserPassword = tk.Entry(master=self,show='*')
        entryIP = tk.Entry(master=self)
        entryIP.insert(0,"127.0.0.1")
        entryPort = tk.Entry(master=self)
        entryPort.insert(0,"8888")

        loginUIElementsArray = [] # array for dynamic configure element
        loginUIElementsArray.insert(0,entryUserName)
        loginUIElementsArray.insert(0,entryUserPassword)
        loginUIElementsArray.insert(0,entryIP)
        loginUIElementsArray.insert(0,entryPort)


        nameLabel = tk.Label(master=self,text="Name:")
        passwordLabel = tk.Label(master=self,text="Password")
        IPLabel = tk.Label(master=self,text="IP:")
        portLabel = tk.Label(master=self,text="Port:")

        buttonSend = tk.Button(master=self,text="Enter",command= lambda: threading.Thread(target=sendUserData,args=(entryUserName.get(),entryUserPassword.get(),entryIP.get(),entryPort.get(),self,controller)).start())
        loginUIElementsArray.insert(0,buttonSend)


        for i in range(0,len(loginUIElementsArray)):
            self.columnconfigure(i,weight=1)
            self.rowconfigure(i,weight=1)

        nameLabel.grid(row=1,column=0)
        entryUserName.grid(row=1,column=1)

        passwordLabel.grid(row=2,column=0)
        entryUserPassword.grid(row=2,column=1)

        IPLabel.grid(row=3,column=0)
        entryIP.grid(row=3,column=1)


        portLabel.grid(row=4,column=0)
        entryPort.grid(row=4,column=1)

        buttonSend.grid(row=5,column=1)


#//TODO: Method to send data to server from login View

def sendUserData(nameText,passwordText,ipText,portText,windowFrame,controller):

    if (nameText != "") and (passwordText != "") and (ipText != "") and (portText != "") and (nameText != " ") and (passwordText != " ") and (ipText != " ") and (portText != " "):
        userData = {"action":"login","name":nameText,"password":passwordText,"ip":ipText,"port":portText}
        jsonUserData = json.dumps(userData).encode('utf8')
        s.sendall(jsonUserData)
        serverResponse = s.recv(1024).decode('utf8')
        print(serverResponse)
        if serverResponse == "Success login":
            controller.show_frame(MainPage)
            global name
            name = nameText

            global currentIP
            currentIP = ipText

            global currentPort
            currentPort = portText

        if serverResponse == "Error login":
            errorUIElement.errorLabel(6,1,windowFrame,"Name or password is wrong")


    else:
        errorUIElement.errorLabel(6,1,windowFrame,"Error!\n Fill all fields")
        


class RegisterPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        backButton = tk.Button(self, text="Back",command=lambda: controller.show_frame(StartPage))
        backButton.grid(row=0,column=0, sticky="nw")

        entryUserName = tk.Entry(master=self)
        entryUserPassword = tk.Entry(master=self,show='*')

        nameLabel = tk.Label(master=self,text="Name:")
        passwordLabel = tk.Label(master=self,text="Password")

        buttonSend = tk.Button(master=self,text="Register",command= lambda: threading.Thread(target=sendNameAndPasswordRegisty,args=(entryUserName.get(),entryUserPassword.get(),self,controller)).start())

        loginUIElementsArray = []
        loginUIElementsArray.insert(0,entryUserName)
        loginUIElementsArray.insert(0,entryUserPassword)
        loginUIElementsArray.insert(0,nameLabel)
        loginUIElementsArray.insert(0,passwordLabel)
        loginUIElementsArray.insert(0,buttonSend)

        for i in range(0,len(loginUIElementsArray)):
            self.columnconfigure(i,weight=1)
            self.rowconfigure(i,weight=1)

        nameLabel.grid(row=1,column=0)
        entryUserName.grid(row=1,column=1)

        passwordLabel.grid(row=2,column=0)
        entryUserPassword.grid(row=2,column=1)

        buttonSend.grid(row=5,column=1)

#//TODO: Method to send data to server from register View

def sendNameAndPasswordRegisty(nameText,passwordText,windowFrame,controller):
    if (nameText != "") and (passwordText != "")  and (nameText != " ") and (passwordText != " "):
        userData = {"action":"register","name":nameText,"password":passwordText}
        jsonUserData = json.dumps(userData).encode('utf8')
        s.sendall(jsonUserData)
        serverResponse = s.recv(1024).decode('utf8')
        print(serverResponse)
        if serverResponse == "Success register":
            controller.show_frame(LoginPage)
        if serverResponse == "Error register":
            errorUIElement.errorLabel(6,1,windowFrame,"This name is busy, use another one")

    else:
        errorUIElement.errorLabel(6,1,windowFrame,"Error!\n Fill all fields")


class MainPage(tk.Frame):
    def __init__(self, parent,controller):
        tk.Frame.__init__(self, parent)

        UIElementsArray = []

        listboxFrame = tk.Frame(master=self,relief=tk.RIDGE,borderwidth=1)
        listboxFrame.grid(row=1,column=0)

        listbox = tk.Listbox(master=listboxFrame)
        listbox.grid(row=2,column=0,sticky="nsew")

        searchUserFrame = tk.Frame(master=self,relief=tk.RIDGE,borderwidth=1)
        searchUserFrame.grid(row=0,column=1)
        UIElementsArray.insert(0,searchUserFrame)

        searchUserIPLabel = tk.Label(master=searchUserFrame,text="IP:")
        searchUserIPEntry = tk.Entry(master=searchUserFrame)
        searchUserNameLabel = tk.Label(master=searchUserFrame,text="Name:")

        writeAddressFrame = tk.Frame(master=self,relief=tk.RIDGE,borderwidth=1)
        writeAddressFrame.grid(row=0,column=2)
        UIElementsArray.insert(0,writeAddressFrame)

        writeMessageFrame = tk.Frame(master=self,relief=tk.RIDGE,borderwidth=1)
        writeMessageFrame.grid(row=0,column=3)
        UIElementsArray.insert(0,writeMessageFrame)

        
        logoutButton = tk.Button(master=self,text="Logout",command= lambda: threading.Thread(target=logoutButtonPressed,args=(controller,)).start())
        logoutButton.grid(row=0,column=0, sticky="nw")
        UIElementsArray.insert(0,logoutButton)

        userInfoButton = tk.Button(master=listboxFrame,text="My info",command= lambda: threading.Thread(target=showMyInfo,args=(listbox,)).start())
        userInfoButton.grid(row=1,column=0,sticky="w")

        onlineUsersButton = tk.Button(master=listboxFrame,text="Online users",command= lambda: threading.Thread(target=onlineUsersRequest,args=(listbox,)).start())
        onlineUsersButton.grid(row=0,column=0,sticky="w")

        searchUserButton = tk.Button(master=searchUserFrame,text="Search users",command=lambda: threading.Thread(target=searchUserByIPorName,args=(searchUserIPEntry.get(),searchUserNameEntry.get(),searchListbox,)).start())
        searchUserNameEntry = tk.Entry(master=searchUserFrame)
        searchListbox = tk.Listbox(master=self)
        searchUserNameEntry.grid(row=0,column=1)
        searchUserButton.grid(row=2,column=1)
        searchUserNameLabel.grid(row=0,column=0)
        searchUserIPLabel.grid(row=1,column=0)
        searchUserIPEntry.grid(row=1,column=1)
        searchListbox.grid(row=1,column=1,sticky="nsew")

        writeAddressButton = tk.Button(master=writeAddressFrame,text="Write address")
        writeAddressIPLabel = tk.Label(master=writeAddressFrame,text="IP:")
        writeAddressPortLabel = tk.Label(master=writeAddressFrame,text="Port:")
        writeAddressIPEntry = tk.Entry(master=writeAddressFrame)
        writeAddressPortEntry = tk.Entry(master=writeAddressFrame)
        writeAddressIPLabel.grid(row=0,column=0)
        writeAddressIPEntry.grid(row=0,column=1)
        writeAddressPortLabel.grid(row=1,column=0)
        writeAddressPortEntry.grid(row=1,column=1)
        writeAddressButton.grid(row=2,column=1)

        startMessageWithUserButton = tk.Button(master=writeMessageFrame,text="Start chat")
        startMessageEntry = tk.Entry(master=writeMessageFrame)
        startMessageLabel = tk.Label(master=writeMessageFrame,text="User name:")
        startMessageLabel.grid(row=0,column=0)
        startMessageEntry.grid(row=0,column=1)
        startMessageWithUserButton.grid(row=1,column=1)



        for i in range(0,len(UIElementsArray)):
            self.columnconfigure(i,weight=1)
            self.rowconfigure(i,weight=1)
        



def logoutButtonPressed(controller):
    controller.show_frame(StartPage)
    global name
    setOffineData = {"action":"set online","name":name,"online":0}
    jsonUserData = json.dumps(setOffineData).encode('utf8')
    s.sendall(jsonUserData)

def showMyInfo(listbox):
    global name
    global currentIP
    global currentPort

    array = []
    array.insert(0,"Name:%s" % (name))
    array.insert(0,"IP:%s" % (currentIP))
    array.insert(0,"Port:%s" % (currentPort))

    listbox.delete(0,tk.END)

    for text in array:
        listbox.insert(0,text)


def onlineUsersRequest(onlineListbox):
    userData = {"action":"Request:online users"}
    jsonUserData = json.dumps(userData).encode('utf8')
    s.sendall(jsonUserData)
    serverResponse = s.recv(1024).decode('utf8')
    onlineUsersArray = serverResponse.split(',')
    print(onlineUsersArray)

    global name
    print("\n Current name is %s" %(name))

    onlineListbox.delete(0,tk.END)

    for onlineUser in onlineUsersArray:
        onlineListbox.insert(0,onlineUser)


def searchUserByIPorName(ipText,nameText,searchListbox):
    userData = {}
    if nameText != "" and nameText != " " and (ipText == "" or ipText == " "):
        print("name")
        userData = {"action":"Request:search user","name":nameText}
    elif ipText != "" and ipText != " " and (nameText == "" or nameText == " "):
        print("ip")
        userData = {"action":"Request:search user","ip":ipText}
    elif nameText != "" and nameText != " " and ipText != "" and ipText != " ":
        print("name and ip")
        userData = {"action":"Request:search user","ip":ipText,"name":nameText}
    
    else:
        return None

    jsonUserData = json.dumps(userData).encode('utf8')
    s.sendall(jsonUserData)

    serverResponse = s.recv(1024).decode('utf8')
    print(serverResponse)
    searchedUserinfoArray = serverResponse.split(',')

    searchListbox.delete(0,tk.END)

    for searchedUser in searchedUserinfoArray:
        searchListbox.insert(0,searchedUser)


    


def on_closing_Window():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        global name
        setOffineData = {"action":"set online","name":name,"online":0} # to set 0 in db when application is closed and the user is offline
        jsonUserData = json.dumps(setOffineData).encode('utf8')
        s.sendall(jsonUserData)
        app.destroy()


#//TODO: Create Application



name = "no name"
currentIP = ""
currentPort = ""

app = ApplicationRoot()
app.protocol("WM_DELETE_WINDOW", on_closing_Window)
app.title("Messenger")
app.geometry("1000x500")
app.mainloop()
