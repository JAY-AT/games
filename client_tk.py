import socket
import threading
import json
import sys
import time
import math
import tkinter as tk

if len(sys.argv) < 3:
    print("Usage: python client_tk.py SERVER_IP SERVER_PORT")
    sys.exit(1)

SERVER = sys.argv[1]
PORT = int(sys.argv[2])

WIDTH, HEIGHT = 800, 600

# ---------------- Networking ----------------
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

# ---------------- Client ----------------
class Client:
    def __init__(self, root):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER, PORT))
        print("Connected to server", SERVER, PORT)

        self.player_id = None
        self.state = {'players':{}, 'bullets':{}}
        self.lock = threading.Lock()
        self.input_state = {'up':False,'down':False,'left':False,'right':False,'shoot':False,'angle':0}

        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='black')
        self.canvas.pack()

        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.bind('<Motion>', self.on_mouse_move)
        self.root.bind('<ButtonPress-1>', lambda e: self.set_shoot(True))
        self.root.bind('<ButtonRelease-1>', lambda e: self.set_shoot(False))

        # listener thread
        t = threading.Thread(target=recv_lines, args=(self.sock,self.on_msg), daemon=True)
        t.start()

        # update loop
        self.last_sent = 0
        self.update_loop()

    def set_shoot(self, val):
        self.input_state['shoot'] = val

    def on_key_press(self, event):
        if event.keysym == 'w': self.input_state['up']=True
        if event.keysym == 's': self.input_state['down']=True
        if event.keysym == 'a': self.input_state['left']=True
        if event.keysym == 'd': self.input_state['right']=True

    def on_key_release(self, event):
        if event.keysym == 'w': self.input_state['up']=False
        if event.keysym == 's': self.input_state['down']=False
        if event.keysym == 'a': self.input_state['left']=False
        if event.keysym == 'd': self.input_state['right']=False

    def on_mouse_move(self, event):
        with self.lock:
            player = self.state['players'].get(self.player_id)
        if player:
            px, py = player['x'], player['y']
        else:
            px, py = WIDTH//2, HEIGHT//2
        self.input_state['angle'] = math.atan2(event.y - py, event.x - px)

    def on_msg(self, msg):
        t = msg.get('type')
        if t == 'welcome':
            self.player_id = msg.get('id')
            print("Assigned id:", self.player_id)
        elif t == 'state':
            payload = msg.get('payload', {})
            with self.lock:
                self.state = payload

    def update_loop(self):
        now = time.time()
        if now - self.last_sent > 1/20.0:
            send_json(self.sock, {'type':'input','payload': self.input_state})
            self.last_sent = now
        self.draw()
        self.root.after(16, self.update_loop)

    def draw(self):
        self.canvas.delete("all")
        with self.lock:
            st = self.state.copy()
    # ---------------- Draw bullets ----------------
        for b in st.get('bullets', {}).values():
            x, y = b['x'], b['y']
            self.canvas.create_oval(x-4, y-4, x+4, y+4, fill='yellow')

    # ---------------- Draw players ----------------
        for pid, p in st.get('players', {}).items():
            x, y = p['x'], p['y']
            color = '#%02x%02x%02x' % tuple(p.get('color',[255,0,0]))
            self.canvas.create_rectangle(x-12, y-12, x+12, y+12, fill=color)
            self.canvas.create_text(x, y-20, text=str(p.get('hp',0)), fill='white', font=('Arial',10,'bold'))
            if pid == self.player_id:
            # Draw facing direction
                ex = x + math.cos(self.input_state['angle'])*20
                ey = y + math.sin(self.input_state['angle'])*20
                self.canvas.create_line(x, y, ex, ey, fill='green', width=2)

    # ---------------- Draw HUD / Legend ----------------
        self.canvas.create_text(10, 10, anchor='nw', text="Controls:", fill='white', font=('Arial',12,'bold'))
        self.canvas.create_text(20, 30, anchor='nw', text="W/A/S/D - Move", fill='white', font=('Arial',10))
        self.canvas.create_text(20, 50, anchor='nw', text="Mouse - Aim", fill='white', font=('Arial',10))
        self.canvas.create_text(20, 70, anchor='nw', text="Left Click / Space - Shoot", fill='white', font=('Arial',10))

    # ---------------- Draw Player HP ----------------
        my_player = st.get('players', {}).get(self.player_id)
        if my_player:
            hp = my_player.get('hp',0)
            self.canvas.create_text(WIDTH-10, 10, anchor='ne', text=f"Your HP: {hp}", fill='red', font=('Arial',12,'bold'))

# ---------------- Main ----------------
root = tk.Tk()
root.title("Multiplayer Shooter (Tkinter)")
client = Client(root)
root.mainloop()
