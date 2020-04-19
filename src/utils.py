from __future__ import print_function
import socket
import sys


def construct_file_str(file):
    file_str = "<{}, {}, {}, {}, {}, {}>".format(file['path'],
                                                 file['type'],
                                                 file['size'],
                                                 file['last_modified'],
                                                 file['ip'],
                                                 file['port'])
    return file_str


# <filename, file path, file type, file size, file last modified date (DD/MM/YY), IP address, port number>
def save_files_dict(all_files, files_str):
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
            'ip': data[5],
            'port': data[6]
        })


def send_msg(conn, msg):
    try:
        conn.sendall(msg.encode())
        print("message sent successfully")
    except socket.error:
        print("failed to send message\n")
        sys.exit(-1)


def save_json():
    pass


if __name__ == '__main__':
    pass
