import socket
import base64
import hashlib
import threading

class WebSocketClient:
    def __init__(self, host='localhost', port=8006):
        self.host = host
        self.port = port

    def generate_accept_key(self, sec_websocket_key):
        magic_guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        combined = sec_websocket_key + magic_guid
        sha1_hash = hashlib.sha1(combined.encode('utf-8')).digest()
        accept_key = base64.b64encode(sha1_hash).decode('utf-8')
        return accept_key

    def start_chat(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        
        sec_websocket_key = base64.b64encode(b"some_random_string").decode('utf-8')
        
        request = (
            "GET / HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {sec_websocket_key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        
        client_socket.send(request.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print("Handshake Response:\n", response)
        
        # Verify handshake
        lines = response.split("\r\n")
        accept_key = ""
        for line in lines:
            if line.startswith("Sec-WebSocket-Accept:"):
                accept_key = line.split(":")[1].strip()
                break
        
        if self.generate_accept_key(sec_websocket_key) != accept_key:
            print("Handshake failed.")
            client_socket.close()
            return
        
        print("Connected to server. Start chatting!\n")

        threading.Thread(target=self.receive_messages, args=(client_socket,), daemon=True).start()

        self.send_messages(client_socket)




    def receive_messages(self,client_socket):
        try:
            while True:
                reply = client_socket.recv(1024)
                if not reply:
                    break
                print(f"\nServer: {reply.decode('utf-8')}\nYou: ", end="")
        except Exception as e:
            print(f"\nConnection error: {e}")
        finally:
            client_socket.close()

    def send_messages(self,client_socket):
        try:
            while True:
                msg = input("You: ")
                if msg == "":
                    continue
                client_socket.send(msg.encode('utf-8'))
        except KeyboardInterrupt:
            print("\nDisconnected from server.")
        finally:
            client_socket.close()
