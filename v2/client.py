import oqs
import socket
import time
import subprocess
import signal

def start_tcpdump():
    # Start tcpdump as a subprocess with packet buffering
    p = subprocess.Popen(["tcpdump", "-U", "-i", "eth0", "-w", "client_capture.pcap"])
    return p

def signal_handler(signum, frame, p):
    p.terminate()
    p.wait()

def log_transfer_statistics(log_file, id, start_time, end_time, data_size):
    interval = f"{start_time:.2f}-{end_time:.2f}"
    transfer = data_size / (1024 ** 2)  # Convert bytes to MBytes
    duration = end_time - start_time
    bitrate = (data_size / 1024) / duration  # Convert bytes/sec to KB/sec
    log_file.write(f"[{id:>3}] {interval:>6} sec {transfer:>6.2f} MBytes {bitrate:>6.1f} KB/sec\n")

def send_data_over_socket(data, host, port, id, log_file):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        start_time = time.time()
        s.sendall(data)
        end_time = time.time()
        log_transfer_statistics(log_file, id, start_time, end_time, len(data))

def receive_data_over_socket(port, id, log_file, buffer_size=4096):
    HOST = '0.0.0.0'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            data = conn.recv(buffer_size)
            end_time = time.time()
            log_transfer_statistics(log_file, id, 0, end_time, len(data))
            return data

def client():
    HOST = 'server'
    PORT = 65432

    kemalg = "Kyber512"
    with oqs.KeyEncapsulation(kemalg) as client, open('client_log.txt', 'a') as log_file:
        public_key = client.generate_keypair()
        
        # Send the actual public key data to the server using a socket
        send_data_over_socket(public_key, HOST, PORT, 5, log_file)
        
        # Receive the ciphertext from the server
        ciphertext = receive_data_over_socket(PORT+1, 6, log_file)
        
        shared_secret_client = client.decap_secret(ciphertext)
        return shared_secret_client

if __name__ == "__main__":
    # Start tcpdump
    tcpdump_process = start_tcpdump()

    # Set signal handlers to ensure graceful shutdown of tcpdump
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, tcpdump_process))
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, tcpdump_process))
    
    shared_secret_client = client()
    print("Client shared secret:", shared_secret_client)

    # Ensure tcpdump process is terminated after client operations
    tcpdump_process.terminate()
    tcpdump_process.wait()
