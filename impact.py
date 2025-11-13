class Impact:
    def __init__(self, x, y, life=0.2):
        self.x = x
        self.y = y
        self.life = life

    def draw(self, canvas):
        canvas.create_oval(self.x-2, self.y-2, self.x+2, self.y+2, fill='orange')
        self.life -= 0.016
