from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

def gen_sk():
    return os.urandom(32)

def encrypt_sk(session_key, peer_public_key_bytes):
    public_key = serialization.load_pem_public_key(peer_public_key_bytes)
    encrypted_key = public_key.encrypt(
        session_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return encrypted_key

def decypt_sk(encrypted_session_key, private_key_bytes):
    private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    session_key = private_key.decrypt(
        encrypted_session_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return session_key

