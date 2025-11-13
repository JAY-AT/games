import math

class Player:
    def __init__(self, pid, name="Player", team="red"):
        self.id = pid
        self.name = name
        self.team = team
        self.x, self.y = 400, 300
        self.angle = 0
        self.hp = 100
        self.ammo = 30
        self.score = 0

    def draw(self, canvas, local_angle=None):
        angle = local_angle if local_angle is not None else self.angle
        size = 15
        color = 'blue' if self.team=='blue' else 'red'

        x1 = self.x + math.cos(angle) * size
        y1 = self.y + math.sin(angle) * size
        x2 = self.x + math.cos(angle + 2.5) * size
        y2 = self.y + math.sin(angle + 2.5) * size
        x3 = self.x + math.cos(angle - 2.5) * size
        y3 = self.y + math.sin(angle - 2.5) * size
        canvas.create_polygon(x1, y1, x2, y2, x3, y3, fill=color)

        # HP bar
        canvas.create_rectangle(self.x-12, self.y-20, self.x-12 + 24*(self.hp/100), self.y-18, fill='green')
        canvas.create_text(self.x, self.y-28, text=self.name, fill='white', font=('Arial',8,'bold'))
