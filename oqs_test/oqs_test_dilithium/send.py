# signature Python example

import oqs
from pprint import pprint
import socket
import time


#######################################################################
# Send 
#######################################################################

def start_tcpdump():
    import subprocess
    subprocess.Popen(["tcpdump", "-i", "eth0", "-w", "client_capture.pcap"])

# send data to specified host at a post
# def send_data_over_socket(data, host, port, id, log_file):


def send_data_over_socket(data, detail, host, port, max_retries=5, retry_delay=2):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        retries = 0
        while retries < max_retries:
            try:
                s.connect((host, port))
                # Connection successful, send data
                s.sendall(data)
                with open("result.txt", 'a') as file:
                    file.writelines(
                        f"Sent {detail} in {retries} attempts.\n")
                    file.close()
                return  # Exit the function after successful send
            except socket.error as e:
                print(
                    f"Failed to connect to {host}:{port}. Retrying in {retry_delay} seconds...")
                retries += 1
                time.sleep(retry_delay)

        print(f"Failed to send data after {max_retries} attempts.")
        with open("result.txt", 'a') as file:
            file.writelines(
                f"Failed to send {detail} after {max_retries} attempts. \n")
            file.close()
        # end_time = time.time()
        # log_transfer_statistics(log_file, id, start_time, end_time, len(data))

if __name__ == "__main__":
    message = "This is the message to sign".encode()

    # create signer and verifier with sample signature mechanisms
    sigalg = "Dilithium2"

    with oqs.Signature(sigalg) as signer:
        # print("\nSignature details:")
        # pprint(signer.details)

        # signer generates its keypair
        signer_public_key = signer.generate_keypair()

        # signer signs the message
        signature = signer.sign(message)

        # send message, signature, and public key to receiver

        send_data_over_socket(message, "Message", "receiver", 5201)
        send_data_over_socket(signature, "Signature", "receiver", 5202)
        send_data_over_socket(signer_public_key, "Public Key", "receiver", 5203)

