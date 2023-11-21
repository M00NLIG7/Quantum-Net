import oqs
import socket
import time
from datetime import datetime

# def receive_data_over_socket(port, id, log_file, buffer_size=4096):


def receive_data_over_socket(port, log_file, type, buffer_size=6144, timeout=12):
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
                    f"{datetime.now()}: Timeout while receiving {type}\n")
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
        log_file.write(
            f"{datetime.now()}: An error occurred: while receiving {type}\n")
        return None


# message signed by sender
# message = "This is the message to sign".encode()
# create signer with sample signature mechanisms


if __name__ == "__main__":
    sigalg = "Dilithium5"

    # receive connection from sender on sequential ports for message, signature, and public key in that order
    while (True):
        with open("results.txt", 'a') as log_file:

            message = receive_data_over_socket(
                5201, log_file=log_file, type='message')

            if not message:
                log_file.writelines(
                    f"{datetime.now()}: Completion Type: message_received, FAILURE\n")

            # print(f'Message: \n{message}', flush=True)
            signature = receive_data_over_socket(
                5202, log_file=log_file, type='signature')

            if not signature:
                log_file.writelines(
                    f"{datetime.now()}: Completion Type: signature_received, FAILURE\n")

            # print(f'Signature: \n{signature}', flush=True)

            signer_public_key = receive_data_over_socket(
                5203, log_file=log_file, type='key')

            if not signer_public_key:
                log_file.writelines(
                    f"{datetime.now()}: Completion Type: key_received, FAILURE\n")

            # print(f'key: \n{signer_public_key}', flush=True)

            with oqs.Signature(sigalg) as verifier:

                # check if any of the receivers did not get their content
                try:
                    is_valid = verifier.verify(
                        message, signature, signer_public_key)

                    if is_valid:
                        log_file.writelines(
                            f"{datetime.now()}: Completion Type: verified, SUCCESS\n")
                    else:
                        log_file.writelines(
                            f"{datetime.now()}: Completion Type: verified, FAILURE\n")

                except Exception as e:
                    print(f'{datetime.now()}: ERROR - {e}')

        # print(f"Verification result: {is_valid}\n", flush=True)

        time.sleep(5)
        log_file.close()
