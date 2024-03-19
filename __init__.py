import socket
import threading
import coloredlogs
import logging
import os
from rich import print as rprint
class Config:
    HOST = 'localhost'
    PORT = 8080
    MAX_CLIENTS = 10
    NAME_LENGTH = 20
    MAX_MESSAGE_LENGTH = 1024

# Configure coloredlogs
coloredlogs.install(level='DEBUG')

class ChatroomServer:
    def __init__(self):
        self.clients = []
        self.nicknames = []  # List of nicknames
        self.server_socket = None
        self.lock = threading.Lock()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.server_socket:
            try:
                self.server_socket.bind((Config.HOST, Config.PORT))
                self.server_socket.listen(Config.MAX_CLIENTS)
                logging.info(f"Chatroom server started on {Config.HOST}:{Config.PORT}")

                while True:
                    client_socket, client_address = self.server_socket.accept()
                    logging.info(f"New client connected: {client_address}")
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                    client_thread.start()
            except socket.error as e:
                logging.error(f"Error starting server: {e}")

    def handle_client(self, client_socket):
        self.clients.append(client_socket)

        try:
            nickname = client_socket.recv(Config.NAME_LENGTH).decode().strip()
            self.nicknames.append(nickname)
            logging.info(f"Client nickname: {nickname}")
            client_socket.send("Nickname received".encode())
        except (ConnectionResetError, socket.error):
            self.remove_client(client_socket)
            return

        while True:
            try:
                message = client_socket.recv(Config.MAX_MESSAGE_LENGTH).decode()
                if message:
                    self.broadcast(message, client_socket)
                else:
                    self.remove_client(client_socket)
                    break
            except (ConnectionResetError, socket.error):
                self.remove_client(client_socket)
                break

    def broadcast(self, message, sender_socket):
        with self.lock:
            for client_socket in self.clients:
                if client_socket != sender_socket:
                    try:
                        client_socket.send(message.encode())
                    except socket.error:
                        self.remove_client(client_socket)

    def remove_client(self, client_socket):
        with self.lock:
            if client_socket in self.clients:
                index = self.clients.index(client_socket)
                nickname = self.nicknames[index]
                logging.info(f"Client disconnected: {client_socket.getpeername()}, Nickname: {nickname}")
                self.broadcast(f"Client disconnected: {client_socket.getpeername()}, Nickname: {nickname}", client_socket)
                self.clients.remove(client_socket)
                self.nicknames.remove(nickname)
                client_socket.close()

    def admin_console(self):
        while True:
            command = input()
            if command == "/clients":
                rprint(self.clients)
            elif command == "/nicknames":
                rprint(self.nicknames)
            elif command == "/exit":
                break
            elif command == '/kick_user':
                user = input("Enter user to kick: ")
                if user in self.nicknames:
                    index = self.nicknames.index(user)
                    client_socket = self.clients[index]
                    self.remove_client(client_socket)
                else:
                    print("User not found")
            elif command == '/ban_user':
                user = input("Enter user to ban: ")
                if user in self.nicknames:
                    index = self.nicknames.index(user)
                    client_socket = self.clients[index]
                    self.remove_client(client_socket)
                    self.nicknames.remove(user)
                else:
                    rprint("User not found")
            elif command == '/help':
                rprint("/clients - List of clients")
                rprint("/nicknames - List of nicknames")
                rprint("/exit - Exit admin console")
                rprint("/kick_user - Kick a user")
                rprint("/ban_user - Ban a user")

class ErrorHandler:
    @staticmethod
    def handle_exception(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"An error occurred: {e}")
        return wrapper

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    chatroom_server = ChatroomServer()
    admin_console_thread = threading.Thread(target=chatroom_server.admin_console)
    admin_console_thread.start()
    chatroom_server.start()
