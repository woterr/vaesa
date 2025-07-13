def send_session_handshake(conn, session_id: str, encrypted_sk: bytes):
    sid_bytes = session_id.encode()
    conn.sendall(
        len(sid_bytes).to_bytes(1, 'big') +
        sid_bytes +
        len(encrypted_sk).to_bytes(2, 'big') +
        encrypted_sk
    )

def recv_session_handshake(conn):
    sid_len = int.from_bytes(conn.recv(1), 'big')
    session_id = conn.recv(sid_len).decode()
    sk_len = int.from_bytes(conn.recv(2), 'big')
    encrypted_sk = conn.recv(sk_len)
    return session_id, encrypted_sk
