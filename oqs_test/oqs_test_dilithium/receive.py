import oqs
import socket
import time

# def receive_data_over_socket(port, id, log_file, buffer_size=4096):



def receive_data_over_socket(port, buffer_size=4096):
    HOST = '0.0.0.0'
    data = None 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow the socket to reuse the address
        s.bind((HOST, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            data = conn.recv(buffer_size)
    return data


# message signed by sender
# message = "This is the message to sign".encode()
# create signer with sample signature mechanisms


if __name__ == "__main__":
    sigalg = "Dilithium2"

    # receive connection from sender on sequential ports for message, signature, and public key in that order
    while (True):
        message = receive_data_over_socket(5201)

        if not message:
            with open("result.txt", 'w') as file:
                file.writelines(f"Verification result: no message!")
                file.close()


        signature = receive_data_over_socket(5202)

        if not signature:
            with open("result.txt", 'a') as file:
                file.writelines(f"Verification result: no signature!\n")
                file.close()

        signer_public_key = receive_data_over_socket(5203)

        if not signer_public_key:
            with open("result.txt", 'a') as file:
                file.writelines(f"Verification result: no public key!\n")
                file.close()

        with oqs.Signature(sigalg) as verifier:
            is_valid = verifier.verify(message, signature, signer_public_key)

            with open("result.txt", 'a') as file:
                file.writelines(f"Verification result: {is_valid}\n")
                file.close()
        
        print(f"Verification result: {is_valid}\n", flush=True)


        time.sleep(5)
