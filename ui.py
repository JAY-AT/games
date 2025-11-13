import time

class UI:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.WIDTH = width
        self.HEIGHT = height

    def draw_crosshair(self, mouse_x, mouse_y):
        self.canvas.create_line(mouse_x-10, mouse_y, mouse_x+10, mouse_y, fill='white')
        self.canvas.create_line(mouse_x, mouse_y-10, mouse_x, mouse_y+10, fill='white')

    def draw_hud(self, player):
        self.canvas.create_text(10,10, anchor='nw', text=f"HP: {player.hp}", fill='red', font=('Arial',12,'bold'))
        self.canvas.create_text(10,30, anchor='nw', text=f"Ammo: {player.ammo}", fill='white', font=('Arial',12,'bold'))
        self.canvas.create_text(self.WIDTH-10,10, anchor='ne', text=f"Score: {player.score}", fill='white', font=('Arial',12,'bold'))
        self.canvas.create_text(self.WIDTH//2,10, anchor='n', text=f"Round Timer: {int(time.time()%180)}s", fill='yellow', font=('Arial',12,'bold'))

    def draw_legend(self, height):
        self.canvas.create_text(10, height-60, anchor='nw', text="W/A/S/D - Move", fill='white', font=('Arial',10))
        self.canvas.create_text(10, height-45, anchor='nw', text="Mouse - Aim", fill='white', font=('Arial',10))
        self.canvas.create_text(10, height-30, anchor='nw', text="Left Click / Space - Shoot", fill='white', font=('Arial',10))

    def draw_minimap(self, players, width, height, map_w=150, map_h=100):
        self.canvas.create_rectangle(width-map_w-10, 10, width-10, 10+map_h, outline='white')
        for p in players.values():
            px = width-map_w-10 + (p.x/width)*map_w
            py = 10 + (p.y/height)*map_h
            color = 'blue' if p.team=='blue' else 'red'
            self.canvas.create_oval(px-3, py-3, px+3, py+3, fill=color)
