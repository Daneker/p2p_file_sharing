from __future__ import print_function
import os
import json
import socket
import sys

from utils import send_msg

config = {}
config_file = ""
total_files_list = []
requested_file = ""
shared_file_dir = ""


def get_shared_file_dir():
    shared_dir = ""
    while not os.path.isdir(shared_dir):
        print()
        print("Enter the directory to share: ")
        shared_dir = raw_input()

        if not os.path.isdir(shared_dir):
            print("this directory doesn't seem like a valid directory, try again")

        return shared_dir


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

    if cmd == "HI":
        send_msg(server, "ERROR\n\0")
        return communicate(server, buffer, "ERROR")

    else:
        print("invalid command received")
        sys.exit(-1)


def main():
    global config
    global config_file

    config_file = "config.json"
    if os.path.isfile(config_file):
        with open(config_file, "rb") as file:
            config = json.load(file)
    else:
        config['server_host'] = 'localhost'
        config['server_port'] = 45000
        config['client_host'] = 'localhost'
        config['client_port'] = 0
        # config['shared_file_dir'] = get_shared_file_dir()

        # with open(config_file, "w", encoding="utf8") as file:
        #     json.dump(config, file, sort_keys=True, indent=4, separators=(",", ": "))

    # shared_files = config['shared_file_dir']
    # files_list = [file_ for file_ in os.listdir(shared_files) if
    #               os.path.isfile(os.path.join(shared_files, file_))]

    server = create_conn((config['host'], config['port']))

    buffer = ""

    # send "HELLO" to server
    send_msg(server, "HELLO\n\0")
    print("I HAVE SENT MSG HELLO")
    buffer = communicate(server, buffer, "HELLO")[0]


if __name__ == '__main__':
    main()
