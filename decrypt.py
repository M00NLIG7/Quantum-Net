import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def encrypt_data(data, key):
    iv = get_random_bytes(16)  # 16 bytes for AES block size
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))
    return iv + encrypted_data  # Return IV with ciphertext for decryption

def decrypt_data(encrypted_data, key):
    iv, ciphertext = encrypted_data[:16], encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size)

def derive_key_from_shared_secret(shared_secret):
    return hashlib.sha256(shared_secret).digest()

shared_secret_client = b'Em\xc3\xb31r\xa6rgRQ\xb7m\xb4\xac\x0b\x8b\x0c\x06:K%,\x1b\xf1\x03\xbf\xa4\\\xae\xabl'

key = derive_key_from_shared_secret(shared_secret_client)  # or shared_secret_server
plaintext = b"dkfhjdkfjkdjfkdjfkdjkdfjdkjf"
encrypted_data = encrypt_data(plaintext, key)
print("Encrypted:", encrypted_data)
decrypted_data = decrypt_data(encrypted_data, key)
print("Decrypted:", decrypted_data.decode('utf-8'))

