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
        except ConnectionRefusedError:
            if i < retries - 1:  # i is 0 indexed
                print(f"Connection refused. Retrying in {delay} seconds...")
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


def client():
    HOST = 'server'
    PORT = 65432

    kemalg = "Kyber512"
    with oqs.KeyEncapsulation(kemalg) as client, open('client_log.txt', 'a') as log_file:
        while True:
            public_key = client.generate_keypair()
            
            # Send the actual public key data to the server using a socket
            send_data_over_socket(public_key, HOST, PORT, 5, log_file)
            
            # Receive the ciphertext from the server
            ciphertext = receive_data_over_socket(PORT+1, 6, log_file)
            
            shared_secret_client = client.decap_secret(ciphertext)
            print("Client shared secret:", shared_secret_client, flush=True)
            time.sleep(5)  # Add a small sleep to prevent excessive looping

if __name__ == "__main__":
    time.sleep(5)  # Give the server some time to start up and listen
    client()
