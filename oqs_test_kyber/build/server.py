import oqs
import socket
import time

def send_data_over_socket(data, host, port, id, log_file, retries=5, delay=2):
    for i in range(retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(data)
                return  # Exit if successful
        except (ConnectionRefusedError, BrokenPipeError):
            if i < retries - 1:  # i is 0 indexed
                print(f"Connection issues with {host}. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            else:
                raise


def receive_data_over_socket(port, id, log_file, buffer_size=4096):
    HOST = '0.0.0.0'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Add this line
        s.bind((HOST, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            data = conn.recv(buffer_size)
            return data


def server():
    PORT = 65432
    HOST = '0.0.0.0'
    
    kemalg = "Kyber512"
    print("Starting server...", flush=True)
    with open('server_log.txt', 'a') as log_file:
        while True:
            # Receive the actual public key data from the client using a socket
            public_key = receive_data_over_socket(PORT, 5, log_file)
            
            with oqs.KeyEncapsulation(kemalg) as server:
                ciphertext, shared_secret_server = server.encap_secret(public_key)
                
                # Send the ciphertext back to the client using a socket
                send_data_over_socket(ciphertext, 'client', PORT+1, 6, log_file)
                
                print("Server shared secret:", shared_secret_server, flush=True)
            time.sleep(5)

if __name__ == "__main__":
    server()
