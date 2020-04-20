from __future__ import print_function
import json
import os
import socket
import sys
import time
from threading import Thread
from tkinter import *
import tkinter as tk

try:
    import queue as Queue
except ImportError:
    import Queue

from utils import send_msg
from transfer_gui_main import ParentWindow

config = {}
config_file = ""
searched_files_list = []

searched_file = "hello"
requested_file = "<hello, some_path, pdf, 258, 07/03/2018, localhost, 7773>"
shared_dir = "/home/daneker/PycharmProjects/p2p/src"

shared_files_list = [
    "<hello, some_path, pdf, 258, 07/03/2018, localhost, 7777>",
    "<hello, some_path, jpg, 158, 02/03/2018, localhost, 7773>"
]


def init_conn(addr):
    host, port = addr
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("creating socket init_conn")
    except socket.error:
        print("failed to create socket\n")
        sys.exit(-1)

    try:
        conn.connect((host, port))
        print("connecting init_conn")
    except socket.error:
        print("failed to connect to port: {}\n".format(port))
        print("failed to connect to host: {}\n".format(host))
        sys.exit(-1)

    return conn


def communicate(server, buffer, prev_cmd):
    global config
    global requested_file
    global searched_file
    global searched_files_list

    if "\0" not in buffer:
        msg = server.recv(4096).decode("utf-8")
        print("received message: ", msg)
        buffer += msg
        return communicate(server, buffer, prev_cmd)
    else:
        idx = buffer.index("\0")
        msg = buffer[:idx-1]
        buffer = buffer[idx+1:]

    lines = msg.split("\n")
    fields = lines[0].split(" ")
    cmd = fields[0]
    # print(cmd)
    list_msg = "LIST \n"

    if cmd == "HI":
        # TODO shared file list to be done via GUI
        # while not shared_files_list:
        #     time.sleep(5)

        for file in shared_files_list:
            list_msg += file + "\n"
        list_msg += "\0"
        send_msg(server, list_msg)
        return communicate(server, buffer, "LIST")

    if cmd == "ACCEPTED" or cmd == "NOT FOUND":
        msg = "SEARCH: "
        # TODO need to be handled via GUI
        msg += searched_file + "\n\0"
        send_msg(server, msg)
        return communicate(server, buffer, prev_cmd)

    if cmd == "FOUND:":
        print("received ", cmd)

        for line in lines[1:]:
            searched_files_list.append(line)
            # TODO pass the file data to GUI
            # pass_the_files(searched_files_list)
        return None, buffer
    else:
        print("invalid command received: ", cmd)
        sys.exit(-1)

def give_peer(peer):
    global requested_file

    send_msg(peer, "DOWNLOAD: {}\n\0".format(requested_file))
    buffer = ""

    # parse message
    while "\0" not in buffer:
        buffer += peer.recv(4096)

    idx = buffer.index("\0")
    msg = buffer[:idx - 1]
    buffer = buffer[idx + 1:]

    fields = msg.split()
    cmd = fields[0]

    if cmd == "FILE:":
        print("DOWNLLOADED THE FILE")
        send_msg(peer, "THANKS\n\0")
        peer.close()

    elif cmd == "ERROR":
        return

    else:
        print("invalid command received\n")
        sys.exit(-1)


def download_from_peer(conn, addr):
    buffer = ""

    while True:
        while "\0" not in buffer:
            buffer += conn.recv(4096).decode("utf-8")

        idx = buffer.index("\0")
        msg = buffer[:idx-1]
        buffer = buffer[idx+1:]

        fields = msg.split()
        cmd = fields[0]

        if cmd == "DOWNLOAD:":
            print("SENDED FILE TO DOOWNLOAD")
            return "", ""
        else:
            send_msg(conn, "ERROR\n\0")
            print("undetermined error\n")
            conn.close()
            break
    return


def listen(lhost, lport, queue):
    try:
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("failed to create socket\n")
        sys.exit(-1)

    try:
        lsock.bind((lhost, lport))
    except socket.error:
        print("failed to bind socket\n")
        sys.exit(-1)

    lsock.listen(3)

    lport = lsock.getsockname()[1]
    queue.put((lhost, lport))

    pcount = 0
    while True:
        conn, addr = lsock.accept()
        pthread = Thread(name="p"+str(pcount), target=download_from_peer, args=(conn, addr))

        pthread.daemon = True
        pthread.start()
        pcount += 1


def main():
    global config
    global config_file

    root = tk.Tk()
    App = ParentWindow(root)
    App.start()
    root.mainloop()

    config_file = "config.json"
    if os.path.isfile(config_file):
        with open(config_file, "rb") as file:
            config = json.load(file)
    else:
        config['host'] = 'localhost'
        config['port'] = 45000
        # TODO json_save(config_file, config)

    server = init_conn((config['host'], config['port']))

    buffer = ""

    # send "HELLO" to server
    send_msg(server, "HELLO\n\0")
    print("I HAVE SENT MSG HELLO")
    buffer = communicate(server, buffer, "HELLO")[0]

    # listen to ???
    queue = Queue.Queue()
    # will be returned by GUI(ip and port)
    lhost = "localhost"
    lport = 7773

    lthread = Thread(name="lthread", target=listen, args=(lhost, lport, queue))
    lthread.daemon = True
    lthread.start()

    lhost, lport = queue.get()

    while not requested_file:
        time.sleep(3)

    req_file_data = requested_file.split(", ")
    peer_host = req_file_data[5]
    peer_port = int(req_file_data[6][:-1])

    peer = init_conn((peer_host, peer_port))
    give_peer(peer)


if __name__ == '__main__':
    main()
