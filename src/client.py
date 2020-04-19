from __future__ import print_function
import os
import json
import signal
import socket
import sys

from utils import send_msg

config = {}
config_file = ""
total_files_list = []
requested_file = ""

shared_files_list = [
    "<hello, some_path, pdf, 258, 07/03/2018, 192.168.0.5, 7777>",
    "<hello, some_path, jpg, 158, 02/03/2018, 192.168.0.2, 7773>"
]


def create_conn(addr):
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
        for file in shared_files_list:
            list_msg += file + "\n"
        list_msg += "\0"
        send_msg(server, list_msg)
        return communicate(server, buffer, "LIST")

    if cmd == "ACCEPTED" or cmd == "NOT FOUND":
        msg = "SEARCH: "
        # need to be handled via GUI
        requested_file = "hello"
        msg += requested_file + "\n\0"
        send_msg(server, msg)
        return communicate(server, buffer, "SEARCH")

    if cmd == "FOUND:":
        print("received ", cmd)
        sys.exit(-1)

    else:
        print("invalid command received: ", cmd)
        sys.exit(-1)


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
        config['client_host'] = 'localhost'
        config['client_port'] = 0

        # json_save(config_file, config)

    server = create_conn((config['host'], config['port']))

    buffer = ""

    # send "HELLO" to server
    send_msg(server, "HELLO\n\0")
    print("I HAVE SENT MSG HELLO")
    buffer = communicate(server, buffer, "HELLO")[0]


if __name__ == '__main__':
    main()
