from client.client import WebSocketClient
from server.server import WebSocketServer

if __name__ == "__main__":
    choice = input("Start (s)erver or (c)lient? ")

    if choice.lower() == 's':
        server = WebSocketServer()
        server.start()
    elif choice.lower() == 'c':
        client = WebSocketClient()
        client.start_chat()
    else:
        print("Invalid choice. Please select 's' for server or 'c' for client.")
