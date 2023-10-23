from oqs import KeyEncapsulation
from Crypto.Cipher import AES
import subprocess

def measure_network_speed(data):
    with open('data_to_send', 'wb') as f:
        f.write(data)
    
    result = subprocess.run(["iperf3", "-c", "localhost", "-p", "5201", "-F", "data_to_send"], capture_output=True, text=True)
    print(result.stdout)

def main():
    kem = KeyEncapsulation('Kyber512')
    public_key = kem.generate_keypair()
    
    # Generate a shared secret
    ciphertext, shared_secret = kem.encap_secret(public_key)
    
    # Using the shared secret to encrypt the "Hello World" message using AES
    #cipher = AES.new(shared_secret[:16], AES.MODE_EAX)
    #nonce = cipher.nonce
    #plaintext = b'Hello World!'*1000
    #ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    
    # Sending the encrypted message
    measure_network_speed(public_key)

if __name__ == "__main__":
    main()
