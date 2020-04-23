from __future__ import print_function
import json
import socket
import sys


def construct_file_str(file):
    file_str = "<{}, {}, {}, {}, {}>".format(file['path'],
                                                 file['type'],
                                                 file['size'],
                                                 file['last_modified'],
                                                 file['client'])
    return file_str


def construct_file_str_2(file_list):
    file_str_list = []
    for file in file_list:
        file_str = "<{}, {}, {}, {}, {}>".format(file['path'],
                                                 file['type'],
                                                 file['size'],
                                                 file['last_modified'],
                                                 file['client'])
        file_str_list.append(file_str)
    return file_str_list

# <filename, file path, file type, file size, file last modified date (DD/MM/YY), IP address, port number>
def save_files_dict(all_files, files_str, client_name, clients):
    for file in files_str:
        data = file.split(", ")
        name = data[0][1:]
        if name not in all_files:
            all_files[name] = []
        all_files[name].append({
            'path': data[1],
            'type': data[2],
            'size': data[3],
            'last_modified': data[4],
            'client': client_name
        })
        json_save("files.json", all_files)


def send_msg(conn, msg):
    try:
        conn.sendall(msg.encode())
        print("message sent successfully")
    except socket.error:
        print("failed to send message\n")
        sys.exit(-1)


def json_save(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)

def json_load(file):
    with open(file, "rb") as f:
        json_ = json.load(f)
    return json_


if __name__ == '__main__':
    pass
