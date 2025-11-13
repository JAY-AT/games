import socket, threading, time, math
import tkinter as tk
from network import send_json, recv_lines
from player import Player
from bullet import Bullet
from impact import Impact
from map import Map
from ui import UI

class Client:
    def __init__(self, root, server_ip, port, width=800, height=600):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server_ip, port))
        print("Connected to server", server_ip, port)

        self.root = root
        self.WIDTH, self.HEIGHT = width, height
        self.canvas = tk.Canvas(root, width=width, height=height, bg='black')
        self.canvas.pack()

        self.player_id = None
        self.players = {}   # pid: Player()
        self.bullets = []   # Bullet objects
        self.impacts = []
        self.lock = threading.Lock()
        self.input_state = {'up':False,'down':False,'left':False,'right':False,'shoot':False,'angle':0}
        self.last_sent = 0
        self.last_shot = 0
        self.fire_rate = 0.2

        self.map = Map()
        self.ui = UI(self.canvas, width, height)

        # Tkinter bindings
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.bind('<Motion>', self.on_mouse_move)
        self.root.bind('<ButtonPress-1>', lambda e: self.set_shoot(True))
        self.root.bind('<ButtonRelease-1>', lambda e: self.set_shoot(False))

        # Networking listener
        threading.Thread(target=recv_lines, args=(self.sock,self.on_msg), daemon=True).start()
        self.update_loop()

    def set_shoot(self,val): self.input_state['shoot']=val
    def on_key_press(self,e):
        if e.keysym=='w': self.input_state['up']=True
        if e.keysym=='s': self.input_state['down']=True
        if e.keysym=='a': self.input_state['left']=True
        if e.keysym=='d': self.input_state['right']=True
    def on_key_release(self,e):
        if e.keysym=='w': self.input_state['up']=False
        if e.keysym=='s': self.input_state['down']=False
        if e.keysym=='a': self.input_state['left']=False
        if e.keysym=='d': self.input_state['right']=False
    def on_mouse_move(self,e):
        player = self.players.get(self.player_id)
        px, py = (player.x, player.y) if player else (self.WIDTH//2,self.HEIGHT//2)
        self.input_state['angle'] = math.atan2(e.y-py, e.x-px)

    def on_msg(self,msg):
        t = msg.get('type')
        if t=='welcome':
            self.player_id = msg.get('id')
            self.players[self.player_id] = Player(self.player_id, name="You", team='blue')
        elif t=='state':
            payload = msg.get('payload',{})
            with self.lock:
                for pid, pdata in payload.get('players',{}).items():
                    if pid not in self.players:
                        self.players[pid] = Player(pid, name=f"Player{pid}", team=pdata.get('team','red'))
                    pl = self.players[pid]
                    pl.x, pl.y = pdata.get('x',pl.x), pdata.get('y',pl.y)
                    pl.angle = pdata.get('angle',pl.angle)
                    pl.hp = pdata.get('hp',pl.hp)
                    pl.ammo = pdata.get('ammo',pl.ammo)
                    pl.score = pdata.get('score',pl.score)

    def update_loop(self):
        now = time.time()
        if now - self.last_sent > 1/20.0:
            send_json(self.sock, {'type':'input','payload': self.input_state})
            self.last_sent = now

        # Shooting
        if self.input_state['shoot'] and (now - self.last_shot)>self.fire_rate:
            if self.player_id:
                p = self.players.get(self.player_id)
                if p:
                    angle = self.input_state['angle']
                    self.bullets.append(Bullet(p.x+math.cos(angle)*20, p.y+math.sin(angle)*20,
                                               math.cos(angle)*10, math.sin(angle)*10, team=p.team))
            self.last_shot = now

        # Move bullets and impacts
        new_bullets = []
        for b in self.bullets:
            b.move()
            if self.map.check_collision(b.x, b.y) or not (0<=b.x<=self.WIDTH and 0<=b.y<=self.HEIGHT):
                self.impacts.append(Impact(b.x,b.y))
                continue
            hit_player = False
            for pid, pl in self.players.items():
                if pid==self.player_id: continue
                if abs(b.x-pl.x)<12 and abs(b.y-pl.y)<12:
                    self.impacts.append(Impact(b.x,b.y))
                    pl.hp = max(0, pl.hp-10)
                    hit_player = True
                    break
            if not hit_player: new_bullets.append(b)
        self.bullets = new_bullets

        # Update impacts
        self.impacts = [imp for imp in self.impacts if imp.life>0]

        self.draw()
        self.root.after(16, self.update_loop)

    def draw(self):
        self.canvas.delete("all")
        self.map.draw(self.canvas)
        for b in self.bullets: b.draw(self.canvas, self.players.get(self.player_id,'red').team)
        for imp in self.impacts: imp.draw(self.canvas)
        for pid, p in self.players.items():
            local_angle = self.input_state['angle'] if pid==self.player_id else None
            p.draw(self.canvas, local_angle)
        # Muzzle flash
        p = self.players.get(self.player_id)
        if p and self.input_state['shoot']:
            angle = self.input_state['angle']
            ex, ey = p.x+math.cos(angle)*25, p.y+math.sin(angle)*25
            self.canvas.create_line(p.x,p.y,ex,ey,fill='orange',width=4)
        # UI
        mx = self.root.winfo_pointerx()-self.root.winfo_rootx()
        my = self.root.winfo_pointery()-self.root.winfo_rooty()
        self.ui.draw_crosshair(mx,my)
        self.ui.draw_hud(p)
        self.ui.draw_legend(self.HEIGHT)
        self.ui.draw_minimap(self.players,self.WIDTH,self.HEIGHT)
