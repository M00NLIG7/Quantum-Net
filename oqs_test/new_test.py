import oqs
import subprocess
import time
import os

def send_data_with_iperf3(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)
    
    with open('iperf3_log.txt', 'a') as log_file:
        result = subprocess.run(["iperf3", "-c", "localhost", "-p", "5201", "-F", filename], stdout=log_file, stderr=log_file, text=True)

def receive_data_with_iperf3(filename):
    # Wait for the file to be available (sent by the other party)
    while not os.path.exists(filename):
        time.sleep(1)
    with open(filename, 'rb') as f:
        return f.read()

def client():
    kemalg = "Kyber512"
    with oqs.KeyEncapsulation(kemalg) as client:
        public_key = client.generate_keypair()
        send_data_with_iperf3(public_key, 'public_key_file')
        ciphertext = receive_data_with_iperf3('ciphertext_file')
        shared_secret_client = client.decap_secret(ciphertext)
        return shared_secret_client

def server():
    kemalg = "Kyber512"
    with oqs.KeyEncapsulation(kemalg) as server:
        public_key = receive_data_with_iperf3('public_key_file')
        ciphertext, shared_secret_server = server.encap_secret(public_key)
        send_data_with_iperf3(ciphertext, 'ciphertext_file')
        return shared_secret_server

def main():
    # Start the server
    shared_secret_server = server()

    # Start the client
    shared_secret_client = client()
    
    # Both client and server now have the same shared secret
    assert shared_secret_client == shared_secret_server, "Shared secrets do not match!"
    
    print("Key exchange successful!")

if __name__ == "__main__":
    main()
