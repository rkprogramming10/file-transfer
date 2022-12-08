from pathlib import Path
from threading import Thread
from tkinter import filedialog
from tkinter import *
from tkinter import ttk
import socket
import ftplib
from ftplib import FTP
import os
import ntpath
import time


SERVER = None
PORT = 5000
BUFFER_SIZE = 4096
IP_ADDRESS = '127.0.0.1'
name = None
textArea = None
listbox = None
labelChat = None
textMessage = None

sendingFile = None
downloadingFile = None
fileToDownload = None


def browseFile():
    global textArea, filePathLabel, sendingFile
    try:
        filename = filedialog.askopenfilename()
        filePathLabel.config(text=filename)
        host_name = '127.0.0.1'
        user_name = 'lftpd'
        password = 'lftpd'

        ftp_server = FTP(host_name, user_name, password)
        ftp_server.encoding = 'utf/8'
        ftp_server.cwd('shared_files')
        f_name = ntpath.basename(filename)
        with open(filename, 'rb') as f:
            ftp_server.storbinary('STOR ' + f_name, f)
        
        ftp_server.dir()
        ftp_server.quit()
        message = ('send '+ f_name)
        if message[:4] == 'send':
            print('Please wait........\n')
            textArea.insert(END, '\n' + 'Please wait........')
            textArea.see("end")
            sendingFile = message[5:]
            fileSize = getFileSize('shared_files/' + sendingFile)
            finalMessage = message + ' ' + str(fileSize)
            SERVER.send(finalMessage.encode())
            textArea.insert(END, '\n' + 'file sending in process......')


    except FileNotFoundError:
        print('Cancel button pressed')

def getFileSize(file_name):
    with open(file_name, 'rb') as f:
        chunk = f.read()
        return len(chunk)

def sendMessage():
    global SERVER, textMessage, textArea
    msgToSend = textMessage.get()
    SERVER.send(msgToSend.encode('ascii'))

    textArea.insert(END, '\n' + 'You>' + msgToSend)
    textArea.see("end")
    textMessage.delete(0, END)
    if msgToSend == 'y' or msgToSend == 'Y' :
        textArea.insert(END, '\n' + 'Please wait........')
        textArea.see("end")
        host_name = '127.0.0.1'
        user_name = 'lftpd'
        password = 'lftpd'
        home = str(Path.home())
        downloadPath = home + '/Downloads'
        ftp_server = ftplib.FTP(host_name, user_name, password)
        ftp_server.encoding = 'utf-8'
        ftp_server.cwd('shared_files')
        f_name = fileToDownload
        localFileName = os.path.join(downloadPath, f_name)
        file = open(localFileName, 'wb')
        ftp_server.retrbinary('RETR ' + f_name, file.write)
        ftp_server.dir()
        file.close()
        ftp_server.quit()
        print('File successfully downloaded to path: '+ downloadPath)
        textArea.insert(END, '\n' + 'File successfully downloaded to path: '+ downloadPath)
        textArea.see("end")
        

    
    


def connectWithClient():
    global SERVER, listbox
    text = listbox.get(ANCHOR)
    list_item = text.split(":")
    msg = 'connect '+ list_item[1]
    SERVER.send(msg.encode('ascii'))
    
def disconnectWithClient():
    global SERVER
    text = listbox.get(ANCHOR)
    list_item = text.split(":")
    msg = 'disconnect '+ list_item[1]
    SERVER.send(msg.encode('ascii'))

def receiveMessage():
    global SERVER
    global BUFFER_SIZE
    global fileToDownload
    global downloadingFile, name

    while True:
        chunk = SERVER.recv(BUFFER_SIZE)
        try:
            if ("tiul" in chunk.decode() and "1.0," not in chunk.decode()):
                letter_list = chunk.decode().split(",")
                listbox.insert(letter_list[0], letter_list[0]+":" +
                               letter_list[1]+": "+letter_list[3]+" "+letter_list[5])
                print(letter_list[0], letter_list[0]+":" +
                      letter_list[1]+": "+letter_list[3]+" "+letter_list[5])
            elif chunk.decode() == 'Access granted':
                labelChat.configure(text = '')
                textArea.insert(END, '\n' + chunk.decode('ascii'))
                textArea.see("end")
            elif 'Access declined by' in chunk.decode():
                labelChat.configure(text = '')
                textArea.insert(END, '\n' + chunk.decode('ascii'))
                textArea.see("end")
            elif 'download?' in chunk.decode():
               
                downloadingFile = chunk.decode('ascii').split(' ')[4].strip()
                BUFFER_SIZE = int(chunk.decode('ascii').split(' ')[8])
                textArea.insert(END, '\n' + chunk.decode('ascii'))
                textArea.see("end")
                print(chunk.decode('ascii'))
            elif 'download:' in chunk.decode():
                getFileName = chunk.decode().split(':')
                fileToDownload = getFileName[1]

            else:
                textArea.insert(END, "\n"+chunk.decode('ascii'))
                textArea.see("end")
                print(chunk.decode('ascii'))
        except:
            pass



def showClient():
    global listbox
    listbox.delete(0,"end")
    SERVER.send("show list".encode('ascii'))


def connect_server():
    global SERVER, name, sending_file
    cname = name.get()
    SERVER.send(cname.encode())





def openChatWindow():
    print('\t\t\tIP MESSAGER\n')
    window = Tk()
    window.title('IP Messenger')
    window.geometry('500x500')
    global name, listbox, textArea, labelChat, textMessage, filePathLabel

    nameLabel = Label(window, text='Enter you name', font=('Calibry', 10))
    nameLabel.place(x=10, y=8)
    name = Entry(window, width=30, font=('Calibry', 10))
    name.place(x=120, y=8)
    name.focus()

    connect_serverButton = Button(window, text='connect to chat server', bd=1, font=(
        'Calibry', 10), command=connect_server)
    connect_serverButton.place(x=350, y=8)

    seperator = ttk.Separator(window, orient='horizontal')
    seperator.place(x=0, y=40, relwidth=1, height=0.1)

    labelUser = Label(window, text='Active Users', font=('Calibry', 10))
    labelUser.place(x=10, y=50)

    listbox = Listbox(window, width=67, height=5, font=(
        'Calibry', 10), activestyle='dotbox')
    listbox.place(x=10, y=70)
    scrollbar1 = Scrollbar(listbox)
    scrollbar1.place(relheight=1, relx=1)
    scrollbar1.config(command=listbox.yview)

    connectButton = Button(window, text='Connect', bd=1, font=('Calibry', 10), command=connectWithClient)
    connectButton.place(x=280, y=160)

    refresh=Button(window,text="Refresh",bd=1, font = ("Calibri",10), command = showClient)
    refresh.place(x=200,y=160)

    disconnectButton = Button(
        window, text='Disconnect', bd=1, font=('Calibry', 10), command=disconnectWithClient)
    disconnectButton.place(x=360, y=160)

    labelChat = Label(window, text='Chat', font=('Calibry', 10))
    labelChat.place(x=10, y=190)

    textArea = Text(window, width=67, height=6, font=('Calibry', 10))
    textArea.place(x=10, y=210)

    scrollbar2 = Scrollbar(textArea)
    scrollbar2.place(relheight=1, relx=1)
    scrollbar2.config(command=listbox.yview)

    textMessage = Entry(window, width=43, font=('Calibry', 12))
    textMessage.pack()
    textMessage.place(x=98, y=306)

    sendButton = Button(window, text='Send', bd=1, font=('Calibry', 10), command=sendMessage)
    sendButton.place(x=450, y=305)

    attachButton = Button(window, text='Attach & Send', bd=1, font=('Calibry', 10), command=browseFile)
    attachButton.place(x=10, y=305)

    filePathLabel = Label(window, text='', font=('Calibry', 8))
    filePathLabel.place(x=10, y=340)

    window.mainloop()


def setup():
    global SERVER, PORT, IP_ADDRESS
    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.connect((IP_ADDRESS, PORT))

    received_thread = Thread(target = receiveMessage)
    received_thread.start()
    
    openChatWindow()


setup()
