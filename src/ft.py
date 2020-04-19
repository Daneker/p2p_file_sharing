from __future__ import print_function
import os
import json
import socket
import sys
from threading import Thread

from utils import send_msg

config = {}
config_file = ""
clients_file = ""
clients = {}
conn_clients = {}



def communicate(conn, client, buffer, prev_cmd):
    global config
    global config_file

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

    if cmd == "HELLO":
        config['uoffset'] += 1
        # with open(config_file, "wb+") as file:
        #     json.dump(config, file, sort_keys=True, indent=4, separators=(",", ": "))

        send_msg(conn, "HI\n\0")
        print("I HAVE SENT MSG HI")
        return communicate(conn, client, buffer, "HI")
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
