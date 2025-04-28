import socket
import base64
import hashlib
import threading


class WebSocketServer:
    def __init__(self, host='localhost', port=8006):
        self.host = host
        self.port = port
        self.clients = []

    def generate_key(self, sec_websocket_key):
        magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        combined_key = sec_websocket_key + magic_string
        sha1_hash = hashlib.sha1(combined_key.encode('utf-8')).digest()
        accept_key = base64.b64encode(sha1_hash).decode('utf-8')
        return accept_key

    def handshake(self, client_socket):
        request = client_socket.recv(1024).decode('utf-8')
        lines = request.split('\r\n')
        
        sec_websocket_key = None
        for line in lines:
            if line.startswith("Sec-WebSocket-Key:"):
                sec_websocket_key = line.split(":")[1].strip()
                break
        
        if not sec_websocket_key:
            raise ValueError("Sec-WebSocket-Key not found in the request")
        
        accept_key = self.generate_key(sec_websocket_key)
        
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
        )
        client_socket.send(response.encode('utf-8'))
        print("Handshake complete.")

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(2)
        
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        
        while True:
            client_socket, client_address = server.accept()
            print(f"Connection from {client_address}")
            


            if len(self.clients) >= 2:
                print(f"Rejecting connection from {client_address} (server full).")
                client_socket.send(
                "HTTP/1.1 503 Service Unavailable\r\n"
                "Content-Type: text/plain\r\n"
                "Connection: close\r\n"
                "\r\n"
                "Server is full. Only two clients allowed.\r\n".encode('utf-8')
                )
                client_socket.close()
                continue

            self.handshake(client_socket)
            self.clients.append(client_socket)

            print(self.clients)

            client_thread = threading.Thread(target=self.handle_client,args=(client_socket,))
            client_thread.start()

    def handle_client(self,client_socket):
        try:
            while True:
                message = client_socket.recv(1024)
                if not message:
                    break
                print(f"Received: {message.decode('utf-8')}")
                
                for client in self.clients:
                    if client != client_socket:
                        try:
                            client.send(message)
                        except Exception as e:
                            print(f"Failed to send message to a client: {e}")
                    
        except ConnectionResetError:
            print("Client disconnected.")
        finally:
            client_socket.close()
