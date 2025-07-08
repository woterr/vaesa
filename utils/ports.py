import psutil

def get_ports():
    ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN' and conn.pid:
            proc = psutil.Process(conn.pid)
            if 'python' in proc.name().lower():
                port = conn.laddr.port
                ports.append(port)
    return ports
