import oqs
import socket
import time
from datetime import datetime


def send_data_over_socket(data, host, port, id, log_file, retries=5, delay=2):
    for i in range(1, retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(data)
                return  # Exit if successful
        except Exception as e:
            if i < retries:  # i is 0 indexed
                print(
                    f"{datetime.now()}: Error - {e}: Retrying in {delay} seconds...", flush=True)
                log_file.write(f"{datetime.now()}: Connection refused.\n")
                time.sleep(delay)

    log_file.write(f'{datetime.now()}: Completion Type: key_sent, FAILURE\n')


def receive_data_over_socket(port, id, log_file, buffer_size=4096, timeout=12):
    HOST = '0.0.0.0'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, port))
            s.listen()
            s.settimeout(timeout)  # Set timeout for accepting a connection

            try:
                conn, addr = s.accept()
            except socket.timeout:
                log_file.write(
                    f"{datetime.now()}: Timeout while waiting for a connection\n")
                return None

            with conn:
                # Optionally reset timeout for recv operation
                conn.settimeout(None)
                log_file.write(
                    f"{datetime.now()}: Connection accepted from {addr}\n")
                try:
                    data = conn.recv(buffer_size)
                except socket.timeout:
                    log_file.write(
                        f"{datetime.now()}: Timeout occurred after {timeout} seconds\n")
                    data = None

                return data
    except Exception as e:
        log_file.write(f"{datetime.now()}: An error occurred: {e}\n")
        return None


def client():
    HOST = 'server'
    PORT = 65432

    kemalg = "Kyber512"
    with oqs.KeyEncapsulation(kemalg) as client:
        while True:

            with open('client_logs.txt', 'a') as log_file:
                public_key = client.generate_keypair()

                # Send the actual public key data to the server using a socket
                send_data_over_socket(public_key, HOST, PORT, 5, log_file)

                # Receive the ciphertext from the server
                ciphertext = receive_data_over_socket(PORT+1, 6, log_file)

                if (not ciphertext):
                    log_file.write(
                        f"{datetime.now()}: Completion Type: cipher_received, FAILURE\n")
                    continue

                shared_secret_client = client.decap_secret(ciphertext)

                if (shared_secret_client):
                    log_file.write(
                        f"{datetime.now()}: Completion Type: client_secret, SUCCESS\n")

                # print("Client shared secret:", shared_secret_client, flush=True)

                time.sleep(5)  # Add a small sleep to prevent excessive looping
                log_file.close()


if __name__ == "__main__":
    time.sleep(5)  # Give the server some time to start up and listen
    client()
