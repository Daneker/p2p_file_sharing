from __future__ import print_function
import socket
import sys


def send_msg(conn, msg):
    print("I AM HERE IN SEND MSG")
    try:
        conn.sendall(msg.encode())
        print("message sent successfully")
    except socket.error:
        print("failed to send message\n")
        sys.exit(-1)


if __name__ == '__main__':
    pass
