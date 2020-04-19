from __future__ import print_function
import os
import json
import socket
import sys
from threading import Thread

from utils import send_msg, save_files_dict, construct_file_str

config = {}
config_file = ""
clients_file = ""
clients = {'u1': {'files': []}}
conn_clients = {}

# <filename, file path, file type, file size, file last modified date (DD/MM/YY), IP address, port number>
# filename: <file path, file type, file size, file last modified date (DD/MM/YY), IP address, port number>
all_files = {}


def communicate(conn, client, buffer, prev_cmd):
    global config
    global config_file
    global all_files

    if "\0" not in buffer:
        return "", prev_cmd
    else:
        idx = buffer.index("\0")
        msg = buffer[:idx-1]
        buffer = buffer[idx+1:]

    # message split
    lines = msg.split("\n")
    fields = lines[0].split(" ")
    cmd = fields[0]
    # print(cmd)
    if cmd == "HELLO":
        config['uoffset'] += 1
        # json_save(config_file, config)

        conn_clients[client] = "u"+str(config['uoffset'])

        send_msg(conn, "HI\n\0")
        print("I have sent msg HI")
        return communicate(conn, client, buffer, "HI")
    elif cmd == "LIST":
        if conn_clients[client] not in clients:
            clients[conn_clients[client]] = {}
        clients[conn_clients[client]]['files'] = lines[1:]

        save_files_dict(all_files, lines[1:])
        print(all_files)

        # json_save(clients_file, clients)

        send_msg(conn, "ACCEPTED\n\0")
        print("I have sent msg ACCEPTED")
        return buffer, "ACCEPTED"

    elif cmd == "SEARCH:":
        filename = fields[1]
        if filename in all_files:
            msg = "FOUND: \n"
            prev_cmd = "FOUND"
            for file in all_files[filename]:
                msg += construct_file_str(file) + "\n"
            msg += "\0"
        else:
            msg = "NOT FOUND\n\0"
            prev_cmd = "NOT FOUND"

        send_msg(conn, msg)
        print("I have sent msg FOUND|NOT FOUND.")
        return buffer, prev_cmd

    else:
        print("invalid command was received\n")
        send_msg(conn, "ERROR\n\0")
        sys.exit(-1)


def serve(conn, addr):
    buffer = ""
    prev_cmd = ""

    while True:
        msg = conn.recv(4096).decode("utf-8")
        print("received message: ", msg)
        if len(msg) == 0:
            break
        else:
            buffer += msg

        buffer, prev_cmd = communicate(conn, addr, buffer, prev_cmd)


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
        config['uoffset'] = 0
        # with open(config_file, "w", encoding="utf8") as file:
        #     json.dump(config, file, sort_keys=True, indent=4, separators=(",", ": "))

    # some json trick with clients file


    # creating socket for connection
    try:
        ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("failed to create socket\n")
        sys.exit(-1)

    host = config['host']
    port = config['port']

    # bind socket
    try:
        ssock.bind((host, port))
    except socket.error:
        print("failed to bind socket\n")
        sys.exit(-1)

    # listen for connections
    ssock.listen(3)

    ccount = 0
    while True:
        conn, addr = ssock.accept()
        # creating thread for each client
        cthread = Thread(name="client_"+str(ccount), target=serve, args=(conn, addr))
        cthread.daemon = True
        cthread.start()
        ccount += 1


if __name__ == "__main__":
    main()
