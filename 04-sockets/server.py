#!/usr/bin/env python

""" The server program for chatroom application using socket programming."""

import sys
import time
import socket
import threading

class Server():
    def __init__(self, ip, port):
        # parameters passed to socket() are constants. 
        # AF_INET is the internet family address for IPv4
        # and SOCK_STREAM is the socket type for TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_address = (ip, port)
        self.socket.bind(self.server_address)
        self.socket.listen()

        self.format = "utf-8"
        # length of message used for sending message length
        self.header_length = 10
        self.commands = {"disconnect": "/disconnect", "people": "/people", "private": "/private"}
        # {connection: {"username": username, "address": address, "join_time": join_time}}
        self.clients = {}
        # {"username": [(time, "message")]}
        self.messages = {}
        self.colors = {
                "purple": '\033[95m',
                "cyan": '\033[96m',
                "darkcyan": '\033[36m',
                "blue": '\033[94m',
                "green": '\033[92m',
                "yellow": '\033[93m',
                "red": '\033[91m',
                "bold": '\033[1m',
                "underline": '\033[4m',
                "end": '\033[0m'
                }
       
        timestamp = self.timestamp()
        print("{} [STARTED] Server started on {}:{}".format(timestamp, *self.server_address))
        self.start_accepting()

    def timestamp(self, formatted=True):
        now = time.strftime("%Y-%m-%d %H:%M")
        if formatted:
            formatted_now = self.colors["cyan"] + "[" + now + "]" + self.colors["end"]
            return formatted_now
        else:
            return now

    def start_accepting(self):
        while True:
            try:
                connection, address = self.socket.accept()
                timestamp = self.timestamp(formatted=False)
                thread = threading.Thread(target=self.handle_client, args=[connection, address, timestamp])
                thread.start()
            except KeyboardInterrupt as err:
                timestamp = self.timestamp()
                print("{} [ShuttingDown]".format(timestamp))
                for client in self.clients:
                    client.close()
                    del self.clients[client]
                # self.socket.close()
                sys.exit(1)

    def handle_client(self, connection, address, timestamp):
        username = self.receive_message(connection)
        self.clients[connection] = {"username": username, "address": address, "join_time": timestamp}
        timestamp = self.timestamp()
        print("{} [NEW CONNECTION] {} connected.".format(timestamp, username))
        print("{} [ACTIVE CONNECTIONS] {}".format(timestamp, threading.active_count()-1))

        self.send_message(connection, "{} connected to server with username: {}"\
                .format(timestamp, self.clients[connection]["username"]))

        # send previous messages to the newly connected user
        len_messages = 0
        for user_messages in self.messages.values():
            len_messages += len(user_messages)
        self.send_message(connection, str(len_messages))

        for username, user_messages in self.messages.items():
            for message in user_messages:
                formatted_message = self.colors["cyan"]+'['+"{}".format(message[0])+']'+self.colors["end"]+' '+username+":> "+message[1]
                self.send_message(connection, formatted_message)

        connected = True
        while connected:
            try:
                message = self.receive_message(connection)
                if message == self.commands["disconnect"]:
                    connected = False
                self.send_to_all_clients(connection, message)
            except:
                connected = False

        self.close_connection(connection)

    def receive_message(self, connection):
        while True:
            message_length = connection.recv(self.header_length).decode(self.format)
            message = connection.recv(int(message_length)).decode(self.format)
            return message


    def send_message(self, connection, message):
        try:
            connection.sendall(bytes(f"{len(message):<{self.header_length}}", self.format))
            connection.send(bytes(message, self.format))
        except Exception as err:
            timestamp = self.timestamp()
            print("{} ".format(timestamp) + self.colors["red"] + "[ERROR]" + self.colors["end"], err)

    def send_to_all_clients(self, connection, message):
        unformatted_timestamp = self.timestamp(formatted=False)
        timestamp = self.timestamp()
        username = self.clients[connection]["username"]

        if username in self.messages.keys():
            self.messages[username].append((unformatted_timestamp, message))
        else:
            self.messages[username] = [(unformatted_timestamp, message)]

        user_message = f"{timestamp} {self.colors['yellow']+self.clients[connection]['username']+self.colors['end']}:> {message}"
        # messages.append(user_message)
        print("{}".format(user_message))
        for client_socket in self.clients:
            if connection != client_socket:
                self.send_message(client_socket, user_message)

    def close_connection(self, client_socket):
        print(f"[DISCONNECTION] {self.clients[client_socket]['username']} has disconnected!")
        del self.clients[client_socket]
        client_socket.close()


if __name__ == "__main__":
    # listen on all IPv4 interfaces 
    host = "0.0.0.0"
    # port to listen on (non-privileged ports are > 1023)
    port = 6000
    server = Server(host, port) 
