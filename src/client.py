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

from utils import send_msg, json_save, json_load
# from transfer_gui_main import ParentWindow

config = {}
config_file = ""
searched_files_list = []

searched_file = "hello"
requested_file = "<hello, some_path, pdf, 258, 07/03/2018, u80>"
shared_dir = "/home/daneker/PycharmProjects/p2p/src"

shared_files_list = [
    "<hello, some_path, pdf, 258, 07/03/2018, u80>",
    "<hello, some_path, jpg, 158, 02/03/2018, u81>"
]

client_name = ""

def retrieve_gui_data(gui_data):
    global shared_files_list
    for data in gui_data:
        file_data = "<{}, {}, {}, {}, {}>".format(data[0], data[1], data[2], data[3], data[4])
        shared_files_list.append(file_data)
def search_gui_filename(file):
    global searched_file
    searched_file = file
def get_qui_requested_file(file):
    global requested_file
    requested_file = file


def init_conn(addr):
    host, port = addr
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("creating socket init_conn")
    except socket.error:
        print("failed to create socket\n")
        # sys.exit(-1)

    try:
        conn.connect((host, port))
        print("connecting init_conn")
    except socket.error:
        print("failed to connect to port: {}\n".format(port))
        print("failed to connect to host: {}\n".format(host))
        # sys.exit(-1)

    return conn


def communicate(server, buffer, prev_cmd):
    global config
    global requested_file
    global searched_file
    global searched_files_list
    global client_name

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
        client_name = fields[1]
        for file in shared_files_list:
            # TODO add client_id to file_data
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

    while "\0" not in buffer:
        buffer += peer.recv(4096).decode("utf-8")
        print("received buffer: ", buffer)
        print("finished receiving")

    idx = buffer.index("\0")
    msg = buffer[:idx]
    buffer = buffer[idx + 1:]

    fields = msg.split()
    cmd = fields[0]
    if cmd == "FILE:":
        print("DOWNLLOADED THE FILE")

        file_data = fields[1].encode()

        # TODO get from GUI
        file_to_save = open(shared_dir + "/" + "sample.txt", "wb")
        file_to_save.write(file_data)
        file_to_save.close()

        send_msg(peer, "THANKS\n\0")
        # peer.close()

    elif cmd == "ERROR":
        print("here in ERROR")
        return

    else:
        print("invalid command received: \n", cmd)
        # sys.exit(-1)
        return


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
            print("SENT FILE TO DOOWNLOAD")

            msg = "FILE: \n"
            conn.send(msg.encode())
            file_ = "/home/daneker/PycharmProjects/p2p/" + "sample.txt"
            file__ = open(file_, "rb")
            print("my file: ", file__)

            file_buffer = ""
            file_buffer = file__.read(1024)
            print("file_buffer: ", file_buffer)
            while file_buffer:
                print(file_buffer)
                conn.send(file_buffer)
                file_buffer = file__.read(1024)

            conn.send("\0".encode())
            file__.close()
            break
        else:
            send_msg(conn, "ERROR\n\0")
            print("undetermined error\n")
            conn.close()
            break
        print("HERE AFTER download")
    # return


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
    global client_name

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
    cconfig = json_load("clients.json")
    # lhost = cconfig[client_name]['host']
    # lport = cconfig[client_name]['port']+1

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
