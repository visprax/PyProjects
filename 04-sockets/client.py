#!/usr/bin/env python3

""" The client program for chatroom application using socket programming."""

import sys
import time
import socket
from threading import Thread

class Client():
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (ip, port)
        self.socket.connect(self.server_address)

        self.format = "utf-8"
        self.header_length = 10
        self.commands = {"disconnect": "/disconnect", "people": "/people", "private": "/private"}
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
        self.username = input("{} Enter your username:> ".format(timestamp))
        self.send_message(self.username)
        
        # receive the handshake message and the past messages 
        handshake_message = self.receive_message()
        print(handshake_message)
        num_past_messages = self.receive_message()
        for _ in range(int(num_past_messages)):
            print(self.receive_message())

        # start receiving current messages
        thread = Thread(target=self.receive_realtime_messages)
        # kill this thread if the main thread killed
        thread.daemon = True
        thread.start()

        # start sending messages
        self.start_messaging()

    def timestamp(self, formatted=True):
        now = time.strftime("%Y-%m-%d %H:%M")
        if formatted:
            formatted_now = self.colors["cyan"] + "[" + now + "]" + self.colors["end"]
            return formatted_now
        else:
            return now

    def send_message(self, message):
        message_length = "{}".format(len(message))
        self.socket.send(bytes(message_length, self.format))
        self.socket.send(bytes(message, self.format))

    def receive_message(self):
        while True:
            message_length = self.socket.recv(self.header_length).decode(self.format)
            if message_length:
                message = self.socket.recv(int(message_length)).decode(self.format)
                return message

    def receive_realtime_messages(self):
        while True:
            message = self.receive_message()
            print(message)

    def start_messaging(self):
        connected = True
        while connected:
            try:
                timestamp = self.timestamp()
                message = input("{} :> ".format(timestamp))
                self.send_message(message)
                if message == self.commands["disconnect"]:
                    connected = False
            except:
                connected = False

        self.close_connection()
    
    def close_connection(self):
        timestamp = self.timestamp()
        print("{} [DISCONNECTING]".format(timestamp))
        self.socket.close()
        sys.exit(1)



if __name__ == "__main__":
    host = "0.0.0.0"
    port = 6000
    client = Client(host, port)
