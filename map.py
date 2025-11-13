class Map:
    def __init__(self):
        # walls: x1,y1,x2,y2
        self.walls = [(200,100,250,400),(500,200,550,500),(100,450,300,480),(600,50,650,300)]

    def draw(self, canvas):
        for w in self.walls:
            canvas.create_rectangle(*w, fill='gray')

    def check_collision(self, x, y):
        for w in self.walls:
            if w[0]<=x<=w[2] and w[1]<=y<=w[3]:
                return True
        return False
