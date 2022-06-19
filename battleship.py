from pygame import *
import random


class UNIT:
    def __init__(self, size: tuple, side: int, tp: str, coord: tuple, img: str, deadImage):
        # Initialize values
        self.coord = coord  # Uses 0-9 x 0-9 grid (aka uses grid)
        self.size = size    # Uses grid
        self.side = side    # int from 0-1, acts as index
        self.name = f'{tp}{side}'  # DLT
        # img is a list of the unit's image, and its rotated version. Rotate acts as the index for this list.
        self.img = image.load('Ships/' + img)
        self.img = [self.img, transform.rotate(self.img, 90)]
        self.rotate = 0
        self.hitbox = self.img[0].get_rect(topleft=(self.coord[0] * 70, self.coord[1] * 70))
        self.drag = False
        self.health = size[0] * size[1]
        self.isDead = False
        # Same structure as img
        self.deadImage = image.load('Ships/' + deadImage)
        self.deadImage = [self.deadImage, transform.rotate(self.deadImage, 90)]

    # Return - Unit being dragged
    def checkClick(self, click):
        # Rotate on right click
        if click.button == 3 and self.drag:
            self.size = (self.size[1], self.size[0])
            self.rotate = 1 - self.rotate

        # On left click:
        elif click.button == 1:
            # If unit is already dragged, try placing.
            if self.drag:

                if self.place(False):
                    return None
                else:
                    return self
            # Else, start dragging unit.
            elif self.hitbox.collidepoint(click.pos):
                self.pickup()
                return self

    # Draw is used in menu 0 and 1, but only in 1 when the unit is dead.
    # When being dragged, unit.draw() returns temporary coordinates.
    def draw(self, dead=False):
        if not dead:
            # If being dragged, use mouse coordinates.
            if self.drag:
                # Get mouse coords, and convert them to 0-9 grid coords for snapping.
                x, y = mouse.get_pos()
                x //= 70
                y //= 70
                # Prevents x, y from being outside of grid.
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

    # Places and stores data of unit. Allows for randomized placement.
    def place(self, Random):
        # If random is enabled, choose rotation, and generate random position within size constraints.
        if Random:
            self.rotate = random.randint(0, 1)
            if self.rotate:
                self.size = (self.size[1], self.size[0])
            self.coord = tuple([random.randint(0, 10 - self.size[i]) for i in range(2)])

        else:
            self.coord = self.draw()  # Get temporary coordinates from draw()

        # Start with True, then check every occupying square of unit for other units. Return false if occupied.
        available = True
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if GRIDS[self.side][j + self.coord[1]][i + self.coord[0]] != self and \
                        GRIDS[self.side][j + self.coord[1]][i + self.coord[0]] is not None:
                    available = False
        if available:
            # Resets hitbox for placement button to ship's new location
            self.hitbox = self.img[self.rotate].get_rect(topleft=(self.coord[0] * 70, self.coord[1] * 70))
            # Loops through all the now occupied squares, and sets them to occupied.
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    GRIDS[self.side][j + self.coord[1]][i + self.coord[0]] = self
            self.drag = False        # Set dragging status to false.
            return True              # If the place is successfully placed, return True.
        elif Random:
            self.place(True)

    # Removes any data of item from grid, enables drag.
    def pickup(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                try:
                    GRIDS[self.side][j + self.coord[1]][i + self.coord[0]] = None
                except IndexError:
                    pass
        self.drag = True

    # Removes health, declares death if necessary.
    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.isDead = True

    # DLT
    def __str__(self):
        return self.name

    # DLT
    __repr__ = __str__


# Paratrooper - 1x2
class PA(UNIT):
    # Initializes unit, and special dragging image.
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 2), side, 'pa', (12, 5), 'PARA.png', 'Dpara.png')
        self.dragImage = image.load('Ships/dragPara.png')
        self.dragImage = [self.dragImage, transform.rotate(self.dragImage, 90)]

    # Copied from UNIT for drag picture
    def draw(self, dead=False):
        if self.drag:
            x, y = mouse.get_pos()
            x //= 70
            y //= 70

            if x + self.size[0] > 9:
                x = 10 - self.size[0]
            if y + self.size[1] > 9:
                y = 10 - self.size[1]

            win.blit(self.dragImage[self.rotate], (x * 70, y * 70))
            return x, y

        else:
            return UNIT.draw(self, dead)


# Platoon - 1x3
class PT(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 3), side, 'pt', (13, 0), 'platoon.png', 'Dart_plat.png')


# Artillery - 1x3
class AT(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 3), side, 'at', (12, 0), 'artillery.png', 'Dart_plat.png')


# Tank - 2x2
# Ability - On first hit taken, owner takes ane extra shot
class TK(UNIT):
    # Diff: Removes rotation after init.
    def __init__(self, side: int):
        UNIT.__init__(self, (2, 2), side, 'tk', (12, 3), 'tank.png', 'Dtank.png')
        self.img = [self.img[0], self.img[0]]
        self.Power = False

    # If no argument is given, return current status. Else, set new status.
    def power(self, Power=None):
        if Power is None:
            return self.Power
        else:
            self.Power = Power


# War Train - 1x5
class WT(UNIT):
    def __init__(self, side: int):
        UNIT.__init__(self, (1, 5), side, 'wt', (13, 5), 'WARTRAIN.png', 'Dtrain.png')


# General class for any button-like object.
class Button:
    # Image is optional. Allows for height and width as well.
    def __init__(self, topleft: tuple, img: [str, tuple], result=True):
        if type(img) == str:
            self.img = image.load(img)
            self.hitbox = self.img.get_rect(topleft=topleft)
        else:
            self.hitbox = Rect(topleft, img)
        self.topleft = topleft
        self.result = result

    def draw(self):
        win.blit(self.img, self.topleft)

    def click(self, click):
        if self.hitbox.collidepoint(click.pos):
            return self.result


# PowerUp section - First Inheritor.
# General class for all powerups.
class PUP(Button):
    IN_GAME = False
    EMPTY_SPOTS = [True, True, True]

    def __init__(self, side: int, pos: tuple, img: str, agro: bool):
        self.select = False
        self.side = side
        Button.__init__(self, pos, "PUPS/" + img)
        self.gimg = image.load("PUPS/g" + img)
        self.ready = True
        self.inUse = False
        self.agro = agro
        self.startpos = pos

    # Activates on click. Different effect depending on stage of game.
    def Select(self, click):
        if self.click(click):
            # If the button is getting clicked, the game is on and the ability is ready, change inUse status.
            if PUP.IN_GAME and self.ready:
                if self.inUse:
                    self.inUse = False
                else:
                    self.inUse = True
            else:
                # If game hasn't started, change selection status of powerup.
                if not PUP.IN_GAME:
                    if self.select:
                        self.select = False
                        PUP.EMPTY_SPOTS[(self.topleft[0] - 900) // (-100)] = True
                        self.Move(self.startpos)
                        POWERS[self.side].remove(self)

                    elif len(POWERS[self.side]) < 3:
                        self.select = True
                        POWERS[self.side].append(self)
                        for spot in range(3):
                            if PUP.EMPTY_SPOTS[spot]:
                                self.Move((900 - 100 * spot, 600))
                                PUP.EMPTY_SPOTS[spot] = False
                                break

    def draw(self):
        # If in use, draw slightly to the right.
        if self.inUse:
            win.blit(self.img, (self.topleft[0]+25, self.topleft[1]))
        else:
            Button.draw(self)

    # Resets button hitbox
    def Move(self, pos):
        Button.__init__(self, pos, (100, 100))


# AOE Damage - 1 use per game
class Barrage(PUP):
    def __init__(self, side):
        PUP.__init__(self, side, (850, 50), "BARRAGE.png", True)
        self.cursor = BIGCROSS("CROSSHAIR.png")  # AOR cursor is selected for this effect

    # Use ability after aiming
    def strike(self):
        self.cursor.strike()

    # DLT
    def __repr__(self):
        return f'Barrage {self.side}'


class SeaCargo(PUP):
    def __init__(self, side):
        PUP.__init__(self, side, (850, 150), "SEACARGO.png", False)

    def __repr__(self):
        return f'SeaCargo {self.side}'


class Scout(PUP):
    def __init__(self, side):
        PUP.__init__(self, side, (850, 250), "SCOUT.png", True)
        self.cursor = LINECROSS("CURSOR.png")

    def strike(self):
        self.cursor.scout()

    def __repr__(self):
        return f'Scout {self.side}'


# Linear Damage - 1 use per game
class Bomb(PUP):
    def __init__(self, side):
        PUP.__init__(self, side, (850, 350), "CARPETBOMB.png", True)
        self.cursor = LINECROSS("CROSSHAIR.png")

    def strike(self):
        self.cursor.strike()

    # DLT
    def __repr__(self):
        return f'Bomb {self.side}'


class Supply(PUP):
    def __init__(self, side):
        PUP.__init__(self, side, (850, 450), "AIRCARGO.png", False)

    def __repr__(self):
        return f'Supply {self.side}'


# General crosshair
class CROSS:
    def __init__(self, img: str, offset=0, OFFSET=(0, 0), Attack=False):
        self.img = image.load(img)
        # offset accounts for minor imperfections. OFFSET accounts for BIGCROSS. Offset accounts for side of board.
        self.offset = offset
        self.OFFSET = OFFSET
        self.Offset = 0
        if Attack:
            self.Offset += 300

    # Takes all offsets into account and draws crosshair
    def draw(self):
        x, y = mouse.get_pos()
        x = ((x-self.offset)//70 + self.OFFSET[0]) * 70 + self.offset
        y = (y//70+self.OFFSET[1]) * 70
        if 0+self.Offset <= x < 700+self.Offset and 0 <= y < 700:
            win.blit(self.img, (x, y))
        return x, y


# AOE cross
class BIGCROSS:
    def __init__(self, img):
        self.CROSSES = [[CROSS("UI/"+img, 20, (i, j), True) for i in range(-1, 2)] for j in range(-1, 2)]

    def draw(self):
        for crosses in self.CROSSES:
            for cross in crosses:
                cross.draw()

    def strike(self):
        X, Y = mouse.get_pos()
        for crosses in self.CROSSES:
            for cross in crosses:
                _X = (X-cross.offset-cross.Offset)//70 + cross.OFFSET[0]
                _Y = Y//70 + cross.OFFSET[1]
                try:
                    strike(_X, _Y)
                except IndexError:
                    pass


class LINECROSS:
    def __init__(self, img: str, offset=0):
        self.img = image.load("UI/"+img)

    def draw(self):
        pos = mouse.get_pos()[1] //70 * 70
        for i in range(10):
            win.blit(self.img, (300+70*i, pos))

    def strike(self):
        pos = mouse.get_pos()[1] // 70
        for i in range(10):
            strike(i, pos)

    def scout(self):
        pos = mouse.get_pos()[1] // 70
        for i in range(10):
            if HITGRIDS[1 - player][pos][i] is None:
                if GRIDS[1 - player][pos][i] is not None:
                    HITGRIDS[1 - player][pos][i] = 1


def strike(x, y):
    if HITGRIDS[1 - player][y][x] is None:
        if GRIDS[1 - player][y][x] is None:
            HITGRIDS[1 - player][y][x] = False
        else:
            HITGRIDS[1 - player][y][x] = True
            GRIDS[1 - player][y][x].hit()
            if GRIDS[1 - player][y][x].name[:-1] == 'tk':
                GRIDS[1 - player][y][x].power(True)
    else:
        return True


def checkWinner():
    for player in range(2):
        for unit in ALL_UNITS[player]:
            if not unit.isDead:
                break
        else:
            return 1-player


# INITIALIZATION
init()
win = display.set_mode((1000, 700))
# creates two grids, 10 by 10, completely filled with None.
GRIDS = [[[None for i in range(10)] for j in range(10)] for k in range(2)]
HITGRIDS = [[[None for i in range(10)] for j in range(10)] for k in range(2)]

BG = image.load('UI/BG.png')
aBG = image.load('UI/AG.png')
PAUSE = image.load('UI/PAUSE.png')
SPLIT = image.load('UI/SPLIT.png')

pBTN = Button((910, 0), 'UI/pauseBTN.png')
RANDOM = Button((770,630),'UI/RANDOM.png')

AIM = CROSS('UI/CROSSHAIR.png', 20, Attack=True)
CUR = CROSS('UI/CURSOR.png')
bAIM = BIGCROSS('CROSSHAIR.png')

HIT = image.load('UI/FIRE.png')
aHIT = image.load('UI/AHIT.png')

MISS = image.load('UI/HOLE.png')
aMISS = image.load('UI/AMISS.png')

BAR = Button((965, 0), 'UI/SLIDE.png')
aBAR = Button((0, 0), 'UI/SLIDE2.png')

MENU = image.load('UI/MENU.png')
newG = Button((380, 340), (220, 90))
HELP = Button((580, 40), (165, 145))

Help = [image.load(f'UI/HELP{i}.png') for i in range(5)]

ResumeG = Button((200,160),(615,60))
Forfeit = Button((330, 440), (365, 65))
# MENU
inMenu = True
while inMenu:
    win.blit(MENU, (0, 0))

    for Event in event.get():
        if Event.type == QUIT:
            quit()
        elif Event.type == MOUSEBUTTONUP:
            if newG.click(Event):
                inMenu = False
            elif HELP.click(Event):
                inHelp = True
                helpSlide = 0
                while inHelp:
                    if helpSlide == 5:
                        inMenu = True
                        inHelp = False
                    else:
                        win.blit(Help[helpSlide], (0, 0))
                        for Event in event.get():
                            if Event.type == QUIT:
                                quit()
                            elif Event.type == KEYUP:
                                if Event.key == K_RETURN:
                                    helpSlide += 1
                    display.update()

    display.update()

# PLACING PHASE
ALL_UNITS = [[PT(i), AT(i), TK(i), PA(i), WT(i)] for i in range(2)]
print(ALL_UNITS)
ALL_POWERS = [[Barrage(i), SeaCargo(i), Scout(i), Bomb(i), Supply(i)] for i in range(2)]
POWERS = [[], []]
for player, units in enumerate(ALL_UNITS):
    Dragging = None
    while True:
        win.blit(BG, (0, 0))
        RANDOM.draw()
        for u in units:
            u.draw()
        Leave = False
        for Event in event.get():
            if Event.type == QUIT:
                quit()
            if Event.type == MOUSEBUTTONUP:
                if RANDOM.click(Event):
                    for r in range(10):
                        for c in range (10):
                            GRIDS[player][r][c] = None
                    for u in units:
                        u.place(True)
                elif Dragging is None:
                    for u in units:
                        Dragging = u.checkClick(Event)
                        if Dragging is not None:
                            break
                else:
                    Dragging = Dragging.checkClick(Event)

            elif Event.type == KEYUP:
                if Event.key == K_RETURN:
                    Leave = True
                    for unit in ALL_UNITS[player]:
                        Leave = unit.coord[0] <= 9
                        if not Leave:
                            print('place all units first')
                            break
                    break
        if Leave:
            break
        display.update()

    # Power Selection mini-phase
    Leave = False
    while True:
        win.blit(BG, (0, 0))
        for u in units:
            u.draw()
        for p in ALL_POWERS[player]:
            p.draw()
        for Event in event.get():
            if Event.type == QUIT:
                quit()
            elif Event.type == MOUSEBUTTONUP:
                for p in ALL_POWERS[player]:
                    p.Select(Event)
            elif Event.type == KEYUP and Event.key == K_RETURN:
                if len(POWERS[player]) == 3:
                    PUP.EMPTY_SPOTS = [True,True,True]
                    Leave = True
                    break
                else:
                    print('Select three powers first')
        display.update()
        if Leave:
            break
    aList = []
    dList = []
    for p in POWERS[player]:
        if p.agro:
            aList.append(p)
            p.Move((150, 700-(150*len(aList))))
        else:
            dList.append(p)
            p.Move((850, 550-(150*len(dList))))
    POWERS[player] = [aList, dList]


# Game Phase
inGame = True
PUP.IN_GAME = True
Winner = None
Menu = 0  # 0 - main; 1 = fire; 2 - settings.
while inGame:
    for player, Units in enumerate(ALL_UNITS):
        inRound = True
        Menu = 0
        Paused = False
        canShoot = True
        if not inGame:
            break
        Between = True
        while Between:
            win.blit(SPLIT, (0, 0))
            for Event in event.get():
                if Event.type == QUIT:
                    quit()
                if Event.type == KEYUP:
                    if Event.key == K_RETURN:
                        inRound = True
                        Between = False
                        break
            display.update()
        while inRound:
            if Menu == 0:
                win.blit(BG, (0, 0))
                BAR.draw()
                pBTN.draw()
                for p in POWERS[player][1]:
                    p.draw()

                for p in POWERS[player][1]:
                    if p.inUse:
                        p.cursor.draw()
                        break
                else:
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

                if Paused:
                    win.blit(PAUSE, (0, 0))
                    for Event in event.get():
                        if Event.type == QUIT:
                            quit()
                        elif Event.type == MOUSEBUTTONUP:
                            if ResumeG.click(Event):
                                Paused = False
                            elif Forfeit.click(Event):
                                quit()  # Change

                for Event in event.get():
                    if Event.type == QUIT:
                        quit()
                    elif Event.type == MOUSEBUTTONUP:
                        if BAR.click(Event):
                            Menu = 1
                        elif pBTN.click(Event):
                            Paused = True
                        for p in POWERS[player][1]:
                            p.Select(Event)
                    elif Event.type == KEYUP and Event.key == K_RETURN and not canShoot:
                        inRound = False

            elif Menu == 1:
                Using_Power = False
                win.blit(aBG, (0, 0))
                aBAR.draw()
                for p in POWERS[player][0]:
                    p.draw()
                for p in POWERS[player][0]:
                    if p.inUse:
                        p.cursor.draw()
                        Using_Power = True
                        break
                else:
                    AIM.draw()
                for row, items in enumerate(HITGRIDS[1 - player]):
                    for column, item in enumerate(items):
                        if item is not None:
                            if item == 1:
                                win.blit(HIT, (70 * column + 300, 70 * row))
                            elif item:
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
                        for p in POWERS[player][0]:
                            if Using_Power:
                                if p.inUse:
                                    p.Select(Event)
                                    break
                            else:
                                p.Select(Event)
                        if aBAR.click(Event):
                            Menu = 0
                        elif (Event.pos[0]) // 70 * 70 >= 280:
                            for p in POWERS[player][0]:
                                if p.inUse:
                                    p.strike()
                                    p.inUse = False
                                    p.ready = False
                                    break
                            else:
                                if canShoot:
                                    x, y = Event.pos
                                    x = (x - 300) // 70
                                    y //= 70
                                    canShoot = strike(x, y)
                                    if ALL_UNITS[player][2].power() and not canShoot:
                                        ALL_UNITS[player][2].power(False)
                                        canShoot = True
                                    break

                        Winner = checkWinner()
                    elif Event.type == KEYUP and Event.key == K_RETURN and not canShoot:
                        inRound = False

            display.update()
            if Winner is not None:
                inGame = False
                inRound = False
                break
