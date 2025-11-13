import json

def send_json(conn, data):
    try:
        conn.sendall((json.dumps(data)+'\n').encode())
    except Exception:
        pass

def recv_lines(sock, callback):
    buffer = b''
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buffer += chunk
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n',1)
                if not line:
                    continue
                try:
                    data = json.loads(line.decode())
                    callback(data)
                except Exception:
                    continue
    except Exception as e:
        print("Listener error:", e)
