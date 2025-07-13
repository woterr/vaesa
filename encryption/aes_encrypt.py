from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

block_size = 16

def pad(data):
    pad_len = block_size - len(data)%block_size
    return data + bytes([pad_len]*pad_len)

def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

def encrypt_data(session_key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    iv = os.urandom(block_size)
    cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded = pad(plaintext)
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    return iv, ciphertext

def decrypt_data(session_key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext_pad = decryptor.update(ciphertext) + decryptor.finalize()
    plaintext = unpad(plaintext_pad)
    return plaintext.decode()