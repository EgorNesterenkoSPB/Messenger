import re
import socket 
import json
import sqlite3
import os
from _thread import *
from tkinter.messagebox import NO
from unittest import result

#//TODO: Create and socket server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_Inet - use ethernet socket, SOCK_STREAM - use TCP protocol
try:
    s.bind(('127.0.0.1',8888)) 
except socket.error as error:
    print(str(error))

s.listen(10)

#//TODO: Set up client and get data

def threaded_client(connection):
    jsonUserData = b'' # for convert data from client to json

    #//TODO: Create database

    #conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn = sqlite3.connect("usersDatabase.db")
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        name TEXT,
        password TEXT,
        ip TEXT,
        port TEXT,
        online INT); 
        """)
    cur.close()
    conn.commit()
    conn.close()
    

    def fetchAllUsers():
        conn = sqlite3.connect("usersDatabase.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM users;")
        results = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()

        return results

    while True:
        data = connection.recv(2048)
        jsonUserData += data
        userData = json.loads(jsonUserData.decode('utf8'))
        print(userData)

        if userData["action"] == "register":  # register user
            users = fetchAllUsers()

            if len(users) == 0:
                conn = sqlite3.connect("usersDatabase.db")
                cur = conn.cursor()

                cur.execute("""INSERT INTO users(name,password,online) VALUES ('%s','%s','%s');""" % (userData["name"],userData["password"],0))
                cur.close()
                conn.commit()
                conn.close()

                connection.sendall("Success register".encode('utf8')) # to send bytes
            else:
                for user in users:
                    if user[0] == userData["name"]:
                        connection.sendall("Error register".encode('utf8'))
                        break
                    else:
                        conn = sqlite3.connect("usersDatabase.db")
                        cur = conn.cursor()

                        cur.execute("""INSERT INTO users(name,password,online) VALUES ('%s','%s','%s');""" % (userData["name"],userData["password"],0))
                        cur.close()
                        conn.commit()
                        conn.close()
                        connection.sendall("Success register".encode('utf8'))
                        break
                        

        if userData["action"] == "login": # login user
            results = fetchAllUsers()
            print(results)
            for user in results:
                if user[0] == userData["name"] and user[1] == userData["password"]:
                    connection.sendall("Success login".encode('utf8'))

                    conn = sqlite3.connect("usersDatabase.db")
                    cur = conn.cursor()
                    cur.execute('''UPDATE users SET online = ? WHERE name = ?''', (1, userData["name"]))
                    cur.execute('''UPDATE users SET ip = ? WHERE name = ?''', (userData["ip"], userData["name"]))
                    cur.execute('''UPDATE users SET port = ? WHERE name = ?''', (userData["port"], userData["name"]))
                    cur.close()
                    conn.commit()
                    conn.close()


                    break
                else:
                    if user == results[len(results)-1]:
                        connection.sendall("Error login".encode('utf8'))
        
        if userData["action"] == "Request:online users":
            results = fetchAllUsers()
            usersName = ""
            for user in results:
                if user[4] == 1:
                    usersName += "%s\n" % user[0]
            connection.sendall(usersName.encode('utf8'))

        if userData["action"] == "set online":
            
            if userData["online"] == 1:
                conn = sqlite3.connect("usersDatabase.db")
                cur = conn.cursor()
                cur.execute('''UPDATE users SET online = ? WHERE name = ?''', (1, userData["name"]))
                cur.close()
                conn.commit()
                conn.close()
            else:
                conn = sqlite3.connect("usersDatabase.db")
                cur = conn.cursor()
                cur.execute('''UPDATE users SET online = ? WHERE name = ?''', (0, userData["name"]))
                cur.close()
                conn.commit()
                conn.close()
        
        if userData["action"] == "Request:search user":
            result = fetchAllUsers()
            userInfo = ""

            if "name" in userData and userData.get("ip") is None:
                print("nameee")
                for user in result:
                    if user[0] == userData["name"]:
                        userInfo = "Online: %s,Port: %s,IP: %s,Name: %s" % (user[4],user[3],user[2],user[0])
                        print(userInfo)
                        connection.sendall(userInfo.encode('utf8'))
                        break
                    else:
                        if user == result[len(result)-1]:
                            connection.sendall("No user with this name".encode('utf8'))

            elif "ip" in userData and userData.get("name") is None:
                print("ipppp")
                for user in result:
                    if user[2] == userData["ip"]:
                        userInfo = "Online: %s,Port: %s,IP: %s,Name: %s" % (user[4],user[3],user[2],user[0])
                        print(userInfo)
                        connection.sendall(userInfo.encode('utf8'))
                        break
                    else:
                        if user == result[len(result)-1]:
                            connection.sendall("User with this ip not found".encode('utf8'))
            elif "name" in userData and "ip" in userData:
                print("nameee and ippp")
                for user in result:
                    if user[0] == userData["name"] and user[2] == userData["ip"]:
                        userInfo = "Online: %s,Port: %s,IP: %s,Name: %s" % (user[4],user[3],user[2],user[0])
                        print(userInfo)
                        connection.sendall(userInfo.encode('utf8'))
                        break
                    else:
                        if user == result[len(result)-1]:
                            connection.sendall("No user with this name or IP".encode('utf8'))
            else:
                print("erorrrring")
                connection.sendall("No user with this name or IP".encode('utf8'))

        #//TODO: Console command handle

        if userData["action"] == "Request:userInfo": # console command from client
            result = fetchAllUsers()
            userInfo = ""

            for user in result:
                if userData["name"] == user[0]:
                    userInfo = "Name: %s\nIP: %s\nPort: %s\nOnline: %s" % (user[0],user[2],user[3],user[4])
                    connection.sendall(userInfo.encode('utf8'))
                    break
        if userData["action"] == "Request:search user terminal":
            result = fetchAllUsers()
            userInfo = ""
            if "name" in userData and userData.get("ip") is None:
                for user in result:
                        if user[0] == userData["name"]:
                            userInfo = "-------------\nName: %s\nIP: %s\nPort: %s\nOnline: %s" % (user[0],user[2],user[3],user[4])
                            print(userInfo)
                            connection.sendall(userInfo.encode('utf8'))
                            break
                        else:
                            if user == result[len(result)-1]:
                                connection.sendall("No user with this name".encode('utf8'))
            elif "ip" in userData and userData.get("name") is None:
                for user in result:
                        if user[2] == userData["ip"]:
                            userInfo = "-------------\nName: %s\nIP: %s\nPort: %s\nOnline: %s" % (user[0],user[2],user[3],user[4])
                            print(userInfo)
                            connection.sendall(userInfo.encode('utf8'))
                            break
                        else:
                            if user == result[len(result)-1]:
                                connection.sendall("No user with this ip".encode('utf8'))

            
        if userData["action"] == "Request:chat connect":
            result = fetchAllUsers()

            for user in result:
                if user[0] == userData["chatBuddyName"]:
                    if user[4] == 1:
                        connection.sendall("Successful connecion")
                        break
                    else:
                        connection.sendall("The user isnt online")
                        break
                else:
                    if user == result[len(result)-1]:
                        connection.sendall("User with this name not found")
                




    
        jsonUserData = b''

        if not data:
            break

    connection.close()



while True:
    connection,addr = s.accept()
    start_new_thread(threaded_client,(connection,))
s.close()



