class Bullet:
    def __init__(self, x, y, dx, dy, team='red'):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.team = team

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, canvas, local_team):
        color = 'yellow' if self.team == local_team else 'red'
        canvas.create_line(self.x, self.y, self.x-self.dx, self.y-self.dy, fill=color, width=2)
