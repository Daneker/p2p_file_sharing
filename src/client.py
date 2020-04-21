from __future__ import print_function
import json
import os
import signal
import socket
import sys
import time
from threading import Thread

try:
    import queue as Queue
except ImportError:
    import Queue

from utils import send_msg, json_save, json_load

config = {}
config_file = "config.json"
client_name = ""
clients = {}
client_file = "clients.json"

searched_files_list = []
shared_files_list = ["</home/daneker/PycharmProjects/p2p/src, json, 52, 21/04/2020, u164>"]

searched_file = "config"
#"</home/daneker/PycharmProjects/p2p/src, json, 52, 21/04/2020, u164>"
requested_file = ""


def retrieve_gui_data(gui_data):
    global shared_files_list
    for data in gui_data:
        file_data = "<{}, {}, {}, {}, {}, ".format(data[0], data[1], data[2], data[3], data[4])
        shared_files_list.append(file_data)


def search_gui_filename(file):
    global searched_file
    searched_file = file


def get_gui_requested_file(file):
    global requested_file
    requested_file = file


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

    if cmd == "HI":
        list_msg = "LIST \n"
        while not shared_files_list:
            time.sleep(5)

        client_name = fields[1]
        for file in shared_files_list:
            file += client_name + ">";
            list_msg += file + "\n"
        list_msg += "\0"
        send_msg(server, list_msg)
        return communicate(server, buffer, "LIST")

    if cmd == "ACCEPTED" or cmd == "NOT_FOUND":
        msg = "SEARCH: "

        while not shared_files_list:
            time.sleep(5)

        msg += searched_file + "\n\0"
        send_msg(server, msg)
        return communicate(server, buffer, prev_cmd)

    if cmd == "FOUND:":
        print("received ", cmd)

        for line in lines[1:]:
            searched_files_list.append(line)
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

    idx = buffer.index("\0")
    msg = buffer[:idx]
    buffer = buffer[idx + 1:]

    fields = msg.split(":\n")
    cmd = fields[0]
    if cmd == "FILE":
        print("DOWNLOADED THE FILE")

        file_data = fields[1].encode()
        req_file_data = requested_file.split(", ")
        downloaded_file_path = "/home/daneker/PycharmProjects/p2p/downloaded_files"
        req_file_type = req_file_data[1]

        file_ = downloaded_file_path + "/" + searched_file + "." + req_file_type

        # TODO get from GUI
        file_to_save = open(file_, "wb")
        file_to_save.write(file_data)
        file_to_save.close()

        send_msg(peer, "THANKS\n\0")
        peer.close()

    elif cmd == "ERROR":
        print("here in ERROR")
        return

    else:
        print("invalid command received: \n", cmd)
        # sys.exit(-1)
        return


def download_from_peer(conn, addr):
    global searched_file
    buffer = ""

    print("download_from_peer()")

    while True:
        print("\nWHILE\n")
        while "\0" not in buffer:
            buffer += conn.recv(4096).decode("utf-8")

        idx = buffer.index("\0")
        msg = buffer[:idx-1]
        buffer = buffer[idx+1:]

        fields = msg.split()
        cmd = fields[0]

        if cmd == "DOWNLOAD:":
            print("SENT FILE TO DOOWNLOAD")
            msg = "FILE:\n"
            conn.send(msg.encode())

            req_file_data = requested_file.split(", ")
            req_file_path = req_file_data[0][1:]
            req_file_type = req_file_data[1]

            file_ = req_file_path + "/" + searched_file + "." + req_file_type
            file__ = open(file_, "rb")

            file_buffer = file__.read(1024)
            while file_buffer:
                conn.send(file_buffer)
                file_buffer = file__.read(1024)

            conn.send("\0".encode())
            file__.close()

        else:
            print("undetermined error BLA BLA\n")
            signal.pause()
            time.sleep(10)
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
        print("\n!!! in LISTEN while loop !!!\n")


def main():
    global config
    global config_file
    global client_name
    global client_file
    global clients

    config_file = "config.json"
    client_file = "clients.json"

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
    lhost = cconfig[client_name]['host']
    lport = cconfig[client_name]['port']+1

    lhost = "127.0.0.1"
    lport = 36360

    lthread = Thread(name="lthread", target=listen, args=(lhost, lport, queue))
    lthread.daemon = True
    lthread.start()

    lhost, lport = queue.get()

    while not requested_file:
        time.sleep(3)

    req_file_data = requested_file.split(", ")
    peer_client = req_file_data[4][:-1]

    print("PEER CLIENT: ", peer_client)
    client = json_load(client_file)[peer_client]

    peer_host = client['host']
    peer_port = int(client['port'])

    peer_host = "127.0.0.1"
    peer_port = 36360

    peer = init_conn((peer_host, peer_port))
    give_peer(peer)

    # download_from_peer(lhost, lport)


# if __name__ == '__main__':
#     main()
