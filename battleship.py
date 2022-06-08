from pygame import *


class UNIT:
    def __init__(self, size: tuple, side: int, tp: str, coord: tuple, img: str):
        self.coord = coord
        self.size = size
        self.side = side
        self.name = f'{tp}{side}'
        self.img = image.load('Ships/' + img)
        self.img = [self.img, transform.rotate(self.img,90)]
        self.rotate = 0
        self.hitbox = self.img[0].get_rect(topleft=(self.coord[0]*70,self.coord[1]*70))
        self.drag = False

    def checkClick(self, click):
        # Rotate on right click
        if click.button == 3 and self.drag:
            self.size = (self.size[1], self.size[0])
            self.rotate = 1-self.rotate

        elif click.button == 1:
            if self.drag:
                available = True
                for i in range(self.size[0]):
                    for j in range(self.size[1]):
                        if GRIDS[self.side][j+self.draw()[1]][i+self.draw()[0]] != self and GRIDS[self.side][j+self.draw()[1]][i+self.draw()[0]] is not None:
                            available = False
                if available:
                    self.place(self.draw())
                    return None
                else:
                    return self

            elif self.hitbox.collidepoint(click.pos):
                self.pickup()
                return self

    def draw(self):
        if self.drag:
            x, y = mouse.get_pos()
            x //= 70
            y //= 70

            if x + self.size[0] > 9:
                x = 10 - self.size[0]
            if y + self.size[1] > 9:
                y = 10 - self.size[1]

            win.blit(self.img[self.rotate], (x * 70, y * 70))
            return x, y

        else:
            win.blit(self.img[self.rotate], (self.coord[0] * 70, self.coord[1] * 70))

    def place(self, coord):
        self.coord = coord
        self.hitbox = self.img[self.rotate].get_rect(topleft=(self.coord[0]*70, self.coord[1]*70))
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                GRIDS[self.side][j + self.coord[1]][i + self.coord[0]] = self
        self.drag = False

    def pickup(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                try:
                    GRIDS[self.side][j + self.coord[1]][i + self.coord[0]] = None
                except IndexError:
                    pass
        self.drag = True

    def __str__(self):
        return self.name

    __repr__ = __str__


# Finish Later - War Train - 1x5
class WT(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 5), side, 'wt', (14, 3), 'train.png')


# Platoon - 1x3
class PT(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 3), side, 'pt', (13, 0), 'platoon.png')


class AT(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 3), side, 'at', (12, 0), 'artillery.png')


# Tank - 2x2
class TK(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (2, 2), side, 'tk', (12, 3), 'tank.png')
        self.img = [self.img[0], self.img[0]]


class Button:
    def __init__(self, topleft: tuple, img, result=True):
        self.img = image.load(img)
        self.topleft = topleft
        self.hitbox = self.img.get_rect(topleft=topleft)
        self.result = result

    def draw(self):
        win.blit(self.img,self.topleft)

    def click(self, click):
        if self.hitbox.collidepoint(click.pos):
            return self.result


class CROSS:
    def __init__(self, img:str, offset=0):
        self.img = image.load(img)
        self.offset = offset

    def draw(self):
        x,y = mouse.get_pos()
        x = x//70*70 + self.offset
        y = y//70*70 + self.offset
        win.blit(self.img,(x,y))


def drawGrid(grid, flip=False):
    x = 0
    if flip:
        x = 300
    win.blit(BG, (0, 0))
    for i in range(9):
        draw.line(win, (255, 255, 255), ((i + 1) * 70 + x, 0), ((i + 1) * 70 + x, 700), 2)
        draw.line(win, (200, 200, 200), (x, (i + 1) * 70), (700 + x, (i + 1) * 70), 2)
    if x:
        draw.line(win, (255, 255, 255), (x, 0), (x, 1000), 2)
    else:
        draw.line(win, (255, 255, 255), (700, 0), (700, 1000), 2)



# INITIALIZATION
init()
win = display.set_mode((1000, 700))
# creates two grids, 10 by 10, completely filled with None.
GRIDS = [[[None for i in range(10)] for j in range(10)] for k in range(2)]
text = font.Font('INVASION2000.TTF', 20)

BG = image.load('UI/BG.png')
AIM = CROSS('UI/CROSSHAIR.png')
CUR = CROSS('UI/CURSOR.png')
HIT = image.load('UI/FIRE.png')
MISS = image.load('UI/HOLE.png')

BAR = Button((881,0), 'UI/SLIDE.png')

# PLACING PHASE
ALL_UNITS = [[PT(i), AT(i), TK(i)] for i in range(2)]
for player, units in enumerate(ALL_UNITS):
    Dragging = None
    while True:

        win.fill((0, 0, 0))
        drawGrid(player)
        for u in units:
            u.draw()

        Leave = False
        for Event in event.get():
            if Event.type == QUIT:
                quit()
            if Event.type == MOUSEBUTTONUP:
                if Dragging is None:
                    for u in units:
                        Dragging = u.checkClick(Event)
                        if Dragging is not None:
                            break

                else:
                    Dragging = Dragging.checkClick(Event)

            if Event.type == KEYUP:
                if Event.key == K_RETURN:
                    Leave = True
                    break
        if Leave:
            break
        display.update()

# Game Phase
inGame = True
Menu = 0  # 0 - main; 1 = fire; 2 - settings.
while inGame:
    for player, Units in enumerate(ALL_UNITS):
        inRound = True
        while inRound:

            if Menu == 0:
                drawGrid(player)
                BAR.draw()
                CUR.draw()
                for unit in Units:
                    unit.draw()

                for Event in event.get():
                    if Event.type == QUIT:
                        quit()
                    elif Event.type == MOUSEBUTTONUP:
                        if BAR.click(Event):
                            Menu = 1

            elif Menu == 1:


            display.update()
