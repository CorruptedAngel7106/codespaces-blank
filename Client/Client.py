import socket
import threading
import coloredlogs
import logging
from colorama import Fore, Style

from rich import print as rprint

class Config:
    HOST = 'localhost'
    PORT = 8080
    NAME_LENGTH = 20
    MAX_MESSAGE_LENGTH = 1024

# Configure coloredlogs
coloredlogs.install(level='DEBUG')

class ChatroomClient:
    def __init__(self):
        self.client_socket = None

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.client_socket:
            try:
                self.client_socket.connect((Config.HOST, Config.PORT))
                logging.info(f"Connected to chatroom server at {Config.HOST}:{Config.PORT}")

                nickname = input("Enter your nickname: ")
                self.client_socket.send(nickname.encode())

                response = self.client_socket.recv(Config.NAME_LENGTH).decode()
                logging.info(response)

                receive_thread = threading.Thread(target=self.receive_messages)
                receive_thread.start()

                while True:
                    message = input()
                    if message:
                        self.client_socket.send(message.encode())
                        logging.info(f"Sent message: {message}")
            except socket.error as e:
                logging.error(f"Error connecting to server: {e}")

    def receive_messages(self):
        while True:
            try:
                if self.client_socket:
                    message = self.client_socket.recv(Config.MAX_MESSAGE_LENGTH).decode()
                    logging.info(f"Received message: {message}")
            except (ConnectionResetError, socket.error):
                logging.error("Disconnected from server")
                break

if __name__ == "__main__":
    chatroom_client = ChatroomClient()
    try:
        chatroom_client.connect()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected. Closing the client.")
    finally:
        if chatroom_client.client_socket:
            chatroom_client.client_socket.close()
