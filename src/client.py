from __future__ import print_function
import json
import os
import socket
import sys
import time
from threading import Thread

try:
    import queue
except ImportError:
    import Queue as queue

from utils import send_msg

config = {}
config_file = ""
total_files_list = []
searched_files_list = []

searched_file = ""
requested_file = "hello.txt"
shared_dir = "/home/daneker/PycharmProjects/p2p/src"

shared_files_list = [
    "<hello, some_path, pdf, 258, 07/03/2018, 192.168.0.5, 7777>",
    "<hello, some_path, jpg, 158, 02/03/2018, 192.168.0.2, 7773>"
]


def retrieve_gui_data(gui_data):
    global shared_files_list
    while not gui_data:
        time.sleep(5)

    for data in gui_data:
        file_data = "<{}, {}, {}, {}, {}>".format(data[0], data[1], data[2], data[3], data[4])
        shared_files_list.append(file_data)


def search_gui_filename(file):
    global searched_file
    while not file:
        time.sleep(2)
        if file:
            break
    searched_file = file

    while not searched_files_list:
        time.sleep(2)
    return searched_files_list


def get_qui_requested_file(file):
    global requested_file
    while not file:
        time.sleep(2)
        if file:
            break
    requested_file = file
    # TODO maybe send downloaded file to gui


def init_conn(addr):
    host, port = addr
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("failed to create socket\n")
        sys.exit(-1)

    try:
        conn.connect((host, port))
    except socket.error:
        print("failed to connect to port\n")
        sys.exit(-1)

    return conn


def communicate(server, buffer, prev_cmd):
    global config
    global total_files_list
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
        while not shared_files_list:
            time.sleep(5)

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
        return communicate(server, buffer, "SEARCH")

    if cmd == "FOUND:":
        print("received ", cmd)

        for line in lines[1:]:
            searched_files_list.append(line)

        # TODO requested file to be chosen from GUI
        while not requested_file:
            time.sleep(2)

        lmsg = "DOWNLOAD: " + requested_file + "\n\0"

        # TODO connect to peer
        # peer = init_conn((peer_ip, peer_port))

        send_msg(server, lmsg)
        communicate(server, buffer, "DOWNLOAD")
    else:
        print("invalid command received: ", cmd)
        sys.exit(-1)


def handle_peer(conn, addr):
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
            file_data = fields[1].split(", ")
            filename = file_data[0]

            if os.path.isfile(filename):
                filesize = file_data[2]
                filetype = file_data[1]
                file = shared_dir + "/" + filename + filetype
                file = open(file, "rb")

                conn.send("FILE: ")
                fbuffer = ""
                fbuffer = file.read(1024)
                while fbuffer:
                    print("sending: " + fbuffer)
                    conn.send(fbuffer)
                    fbuffer += file.read(1024)
                    file.close()
                else:
                    send_msg(conn, "ERROR\n\0")
                    print("failed to send file\n")
                    conn.close()
                    break
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
        pthread = Thread(name="p"+str(pcount), target=handle_peer, args=(conn, addr))

        pthread.daemon = True
        pthread.start()
        pcount += 1


def main():
    global config
    global config_file

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

    # listen to peer client
    queue = Queue.Queue()
    # will be returned by GUI(ip and port)
    lhost = "localhost"
    lport = 0

    lthread = Thread(name="lthread", target=listen, args=(lhost, lport, queue))
    lthread.daemon = True
    lthread.start()

    lhost, lport = queue.get()


if __name__ == '__main__':
    main()
