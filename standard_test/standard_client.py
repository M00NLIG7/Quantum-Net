from Crypto.Cipher import AES
import subprocess

def measure_network_speed(data):
    with open('data_to_send', 'wb') as f:
        f.write(data)
    
    result = subprocess.run(["iperf3", "-c", "localhost", "-p", "5202", "-F", "data_to_send"], capture_output=True, text=True)
    print(result.stdout)

def main():
    key = b'Sixteen byte key'
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(b'Hello World!'*1000)  # Encrypt the same message

    measure_network_speed(ciphertext)

if __name__ == "__main__":
    main()
