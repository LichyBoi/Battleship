from pygame import *


class UNIT:
    def __init__(self, size: tuple, side: int, tp: str, coord: tuple, img: str, deadImage):
        self.coord = coord
        self.size = size
        self.side = side
        self.name = f'{tp}{side}'
        self.img = image.load('Ships/' + img)
        self.img = [self.img, transform.rotate(self.img, 90)]
        self.rotate = 0
        self.hitbox = self.img[0].get_rect(topleft=(self.coord[0] * 70, self.coord[1] * 70))
        self.drag = False
        self.health = size[0] * size[1]
        self.isDead = False
        self.deadImage = image.load(deadImage)
        self.deadImage = [self.deadImage, transform.rotate(self.deadImage, 90)]

    def checkClick(self, click):
        # Rotate on right click
        if click.button == 3 and self.drag:
            self.size = (self.size[1], self.size[0])
            self.rotate = 1 - self.rotate

        elif click.button == 1:
            if self.drag:
                available = True
                for i in range(self.size[0]):
                    for j in range(self.size[1]):
                        if GRIDS[self.side][j + self.draw()[1]][i + self.draw()[0]] != self and \
                                GRIDS[self.side][j + self.draw()[1]][i + self.draw()[0]] is not None:
                            available = False
                if available:
                    self.place(self.draw())
                    return None
                else:
                    return self

            elif self.hitbox.collidepoint(click.pos):
                self.pickup()
                return self

    def draw(self, dead=False):
        if not dead:
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
        else:
            win.blit(self.deadImage[self.rotate], (self.coord[0] * 70 + 300, self.coord[1] * 70))

    def place(self, coord):
        self.coord = coord
        self.hitbox = self.img[self.rotate].get_rect(topleft=(self.coord[0] * 70, self.coord[1] * 70))
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

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.isDead = True

    def __str__(self):
        return self.name

    __repr__ = __str__


# Finish Later - War Train - 1x5
class WT(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 5), side, 'wt', (14, 3), 'train.png', '')


# Platoon - 1x3
class PT(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 3), side, 'pt', (13, 0), 'platoon.png', 'Ships/Dart_plat.png')


class AT(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 3), side, 'at', (12, 0), 'artillery.png', 'Ships/Dart_plat.png')


# Tank - 2x2
class TK(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (2, 2), side, 'tk', (12, 3), 'tank.png', 'Ships/Dtank.png')
        self.img = [self.img[0], self.img[0]]
        self.Power = False
    def power(self, Power=None):
        if Power is None:
            return self.Power
        else:
            self.Power = Power

class Button:
    def __init__(self, topleft: tuple, img:[str,tuple], result=True):
        if type(img) == str:
            self.img = image.load(img)
            self.hitbox = self.img.get_rect(topleft=topleft)
        else:
            self.hitbox = Rect(topleft,img)
        self.topleft = topleft
        self.result = result

    def draw(self):
        win.blit(self.img, self.topleft)

    def click(self, click):
        if self.hitbox.collidepoint(click.pos):
            return self.result


class CROSS:
    def __init__(self, img: str, offset=0):
        self.img = image.load(img)
        self.offset = offset

    def draw(self):
        x, y = mouse.get_pos()
        x = (x - 15) // 70 * 70 + self.offset
        y = y // 70 * 70
        win.blit(self.img, (x, y))
        return x, y


def strike(x, y):
    if HITGRIDS[1 - player][y][x] is None:
        if GRIDS[1 - player][y][x] is None:
            HITGRIDS[1 - player][y][x] = False
        else:
            HITGRIDS[1 - player][y][x] = True
            GRIDS[1 - player][y][x].hit()
            if GRIDS[1-player][y][x].name[:-1] == 'tk':
                GRIDS[1 - player][y][x].power(True)


# INITIALIZATION
init()
win = display.set_mode((1000, 700))
# creates two grids, 10 by 10, completely filled with None.
GRIDS = [[[None for i in range(10)] for j in range(10)] for k in range(2)]
HITGRIDS = [[[None for i in range(10)] for j in range(10)] for k in range(2)]
text = font.Font('INVASION2000.TTF', 20)

BG = image.load('UI/BG.png')
aBG = image.load('UI/AG.png')

AIM = CROSS('UI/CROSSHAIR.png', 20)
CUR = CROSS('UI/CURSOR.png')

HIT = image.load('UI/FIRE.png')
aHIT = image.load('UI/AHIT.png')

MISS = image.load('UI/HOLE.png')
aMISS = image.load('UI/AMISS.png')

BAR = Button((965, 0), 'UI/SLIDE.png')
aBAR = Button((0, 0), 'UI/SLIDE2.png')

MENU = image.load('UI/MENU.png')
newG = Button((380,340),(220,90))
loadG = Button((330,110),(220,75))
HELP = Button((580,40),(165,145))
# MENU
inMenu = True
while inMenu:
    win.blit(MENU,(0,0))

    for Event in event.get():
        if Event.type == QUIT:
            quit()
        elif Event.type == MOUSEBUTTONUP:
            if newG.click(Event):
                inMenu = False
            elif loadG.click(Event):
                print ("Loaded Game")
            elif HELP.click(Event):
                print ("Help")
            else:
                print (Event.pos)

    display.update()
'''for Event in event.get():
                if Event.type == QUIT:
                    quit()
                elif Event.type == MOUSEBUTTONUP:
                    if BAR.click(Event):
                        Menu = 1'''
'''
    draw bg
    loop through buttons:
        if button: do button
        '''

# PLACING PHASE
ALL_UNITS = [[PT(i), AT(i), TK(i)] for i in range(2)]
for player, units in enumerate(ALL_UNITS):
    Dragging = None
    while True:

        win.fill((0, 0, 0))
        win.blit(BG, (0, 0))
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
        Menu = 0
        while inRound:
            if Menu == 0:
                win.blit(BG, (0, 0))
                BAR.draw()
                CUR.draw()
                for unit in Units:
                    unit.draw()
                for row, items in enumerate(HITGRIDS[player]):
                    for column, item in enumerate(items):
                        if item is not None:
                            if item:
                                win.blit(HIT, (70 * column, 70 * row))
                            else:
                                win.blit(MISS, (70 * column, 70 * row))

                for Event in event.get():
                    if Event.type == QUIT:
                        quit()
                    elif Event.type == MOUSEBUTTONUP:
                        if BAR.click(Event):
                            Menu = 1

            elif Menu == 1:
                win.blit(aBG, (0, 0))
                aBAR.draw()
                AIM.draw()
                for row, items in enumerate(HITGRIDS[1 - player]):
                    for column, item in enumerate(items):
                        if item is not None:
                            if item:
                                win.blit(aHIT, (70 * column + 300, 70 * row))
                            else:
                                win.blit(aMISS, (70 * column + 300, 70 * row))
                for unit in ALL_UNITS[1 - player]:
                    if unit.isDead:
                        unit.draw(True)
                for Event in event.get():
                    if Event.type == QUIT:
                        quit()
                    elif Event.type == MOUSEBUTTONUP:
                        if aBAR.click(Event):
                            Menu = 0
                        elif (Event.pos[0]) // 70 * 70 >= 280:
                            x, y = Event.pos
                            x = (x - 300) // 70
                            y //= 70
                            strike(x, y)
                            if ALL_UNITS[player][2].power():
                                ALL_UNITS[player][2].power(False)
                            else:
                                inRound = False

                            break
            display.update()
