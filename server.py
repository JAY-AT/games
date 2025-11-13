import socket
import threading
import json
import time
import math

# ---------------- Server State ----------------
clients = {}  # pid -> player info
next_id = 1
lock = threading.Lock()
bullets = []

# ---------------- Networking ----------------
def send_json(conn, data):
    try:
        conn.sendall((json.dumps(data)+'\n').encode())
    except:
        pass

def broadcast_state():
    state = {'players':{}, 'bullets':[]}
    with lock:
        for pid, p in clients.items():
            state['players'][pid] = {
                'x': p['x'],
                'y': p['y'],
                'angle': p['angle'],
                'hp': p['hp'],
                'team': p['team']
            }
        for b in bullets:
            state['bullets'].append({'x': b['x'], 'y': b['y'], 'dx': b['dx'], 'dy': b['dy'], 'team': b['team']})
        for p in clients.values():
            send_json(p['conn'], {'type':'state','payload':state})

# ---------------- Client Handler ----------------
def handle_client(conn, addr, pid):
    global clients
    print(f"Player {pid} connected from {addr}")
    send_json(conn, {'type':'welcome', 'id': pid})

    while True:
        try:
            line = conn.recv(4096)
            if not line:
                break
            for l in line.split(b'\n'):
                if not l:
                    continue
                data = json.loads(l.decode())
                if data.get('type')=='input':
                    payload = data.get('payload',{})
                    with lock:
                        p = clients[pid]
                        # Simple movement
                        speed = 5
                        if payload.get('up'): p['y'] -= speed
                        if payload.get('down'): p['y'] += speed
                        if payload.get('left'): p['x'] -= speed
                        if payload.get('right'): p['x'] += speed
                        p['angle'] = payload.get('angle', p['angle'])
                        # Shooting
                        if payload.get('shoot') and p['hp']>0:
                            b = {
                                'x': p['x'] + math.cos(p['angle'])*20,
                                'y': p['y'] + math.sin(p['angle'])*20,
                                'dx': math.cos(p['angle'])*10,
                                'dy': math.sin(p['angle'])*10,
                                'team': p['team']
                            }
                            bullets.append(b)
            broadcast_state()
        except:
            break

    print(f"Player {pid} disconnected")
    with lock:
        del clients[pid]
    conn.close()

# ---------------- Bullet Update Loop ----------------
def update_bullets():
    global bullets
    while True:
        with lock:
            new_bullets = []
            for b in bullets:
                b['x'] += b['dx']
                b['y'] += b['dy']
                # Remove bullets out of bounds
                if 0 <= b['x'] <= 800 and 0 <= b['y'] <= 600:
                    # Check collision with players
                    for pid, p in clients.items():
                        if p['team'] != b['team'] and abs(b['x']-p['x'])<12 and abs(b['y']-p['y'])<12:
                            p['hp'] = max(0, p['hp']-10)
                            break
                    else:
                        new_bullets.append(b)
            bullets = new_bullets
        time.sleep(0.016)

# ---------------- Server Main ----------------
HOST = '127.0.0.1'
PORT = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print(f"Server listening on {HOST}:{PORT}")

# Start bullet update thread
threading.Thread(target=update_bullets, daemon=True).start()

while True:
    conn, addr = s.accept()
    with lock:
        pid = str(next_id)
        next_id += 1
        clients[pid] = {'conn': conn, 'x':400, 'y':300, 'angle':0, 'hp':100, 'team':'red'}
    threading.Thread(target=handle_client, args=(conn, addr, pid), daemon=True).start()
