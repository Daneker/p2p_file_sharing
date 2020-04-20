from __future__ import print_function
import json
import os
import socket
import sys
import time
from threading import Thread

try:
    import queue as Queue
except ImportError:
    import Queue

from utils import send_msg

from client import requested_file

def give_peer(peer):
    global requested_file

    send_msg(peer, "DOWNLOAD: {}\n\0", requested_file)
    buffer = ""

    # parse message
    while "\0" not in buffer:
        buffer += peer.recv(4096).decode("utf-8")
        print("received msg: ", buffer)

    idx = buffer.index("\0")
    msg = buffer[:idx - 1]
    buffer = buffer[idx + 1:]

    fields = msg.split()
    cmd = fields[0]

    if cmd == "FILE:":
        # file_size = fields[1]

        # file_to_save = open(sharing_directory + "/" + requested_file, "wb")
        # file_to_save.write(incoming_buffer)
        # file_to_save.close()

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
            print("received msg: ", buffer)

        idx = buffer.index("\0")
        msg = buffer[:idx-1]
        buffer = buffer[idx+1:]

        fields = msg.split()
        cmd = fields[0]

        if cmd == "DOWNLOAD:":
            print("SENDED FILE TO DOWNLOAD")
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


# def retrieve_gui_data(gui_data):
#     global shared_files_list
#     while not gui_data:
#         time.sleep(5)
#
#     for data in gui_data:
#         file_data = "<{}, {}, {}, {}, {}>".format(data[0], data[1], data[2], data[3], data[4])
#         shared_files_list.append(file_data)
#
#
# def search_gui_filename(file):
#     global searched_file
#     while not file:
#         time.sleep(2)
#         if file:
#             break
#     searched_file = file
#
#
# def get_qui_requested_file(file):
#     global requested_file
#     while not file:
#         time.sleep(2)
#         if file:
#             break
#     requested_file = file
#     # TODO maybe send downloaded file to gui