import oqs
import socket
import time
from datetime import datetime


def send_data_over_socket(data, host, port, id, log_file, retries=5, delay=2):
    for i in range(retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(data)

                return  # Exit if successful
        except:
            if i < retries - 1:  # i is 0 indexed
                # print(f"Connection issues with {host}. Retrying in {delay} seconds...", flush=True)
                log_file.write(f'{datetime.now()}: Connection refused.\n')
                time.sleep(delay)
            else:
                log_file.write(
                    f'{datetime.now()}: Completion Type: cipher_sent, FAILURE\n')


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


def server():
    PORT = 65432
    HOST = '0.0.0.0'

    kemalg = "Kyber512"
    print("Starting server...", flush=True)
    with oqs.KeyEncapsulation(kemalg) as server:
        while True:

            with open('server_logs.txt', 'a') as log_file:
                # Receive the actual public key data from the client using a socket
                public_key = receive_data_over_socket(PORT, 5, log_file)
                if (not public_key):
                    log_file.write(
                        f"{datetime.now()}: Completion Type: key_received, FAILURE\n")
                    continue

                ciphertext, shared_secret_server = server.encap_secret(
                    public_key)

                # Send the ciphertext back to the client using a socket
                send_data_over_socket(
                    ciphertext, 'client', PORT+1, 6, log_file)

                if (shared_secret_server):
                    log_file.write(
                        f'{datetime.now()}: Completion Type: server_secret, SUCCESS\n')
                else:
                    log_file.write(
                        f'{datetime.now()}: Completion Type: server_secret, FAILURE\n')

                # print("Server shared secret:", shared_secret_server, flush=True)
                time.sleep(5)
                log_file.close()


if __name__ == "__main__":
    time.sleep(5)
    server()
