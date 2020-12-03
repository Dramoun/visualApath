import pygame
import math
import time
from datetime import datetime

pygame.init()
pygame.display.set_caption('visualApath')

sqSide = 64
fieldSize = 10

topBar = sqSide
timeBoxPos = (212, 33)
resetBoxPos = (424, 33)

res = (sqSide * fieldSize, (sqSide * fieldSize) + topBar)

screen = pygame.display.set_mode(res)
myFont = pygame.font.SysFont("Calibri", int(sqSide / 2))

gameActiveBool = True
gameRunning = False

timeStart = 0
lastTime = 0
sec = 0

def initialGen():
    fieldDic = {}

    for x in range(fieldSize):
        for y in range(fieldSize):
            fieldDic[(x * sqSide, topBar + (y * sqSide))] = {"f": math.inf, "g": math.inf, "h": math.inf,
                                                             "state": "None",
                                                             "parent": tuple}

    return fieldDic


def drawField():
    for pos, items in playField.items():
        pygame.draw.rect(screen, getColorByState(items["state"]), (pos[0] + 1, (pos[1] + 1), sqSide - 2, sqSide - 2))

        if items["f"] not in (math.inf, 0) and items["state"] not in ("start", "end", "wall"):
            drawStr(((pos[0] + (sqSide / 2)), (pos[1] + (sqSide / 2))), items["f"])

        if items["state"] == "start":
            drawStr(((pos[0] + (sqSide / 2)), (pos[1] + (sqSide / 2))), "S")

        # if end bool is ok
        # elif items["state"] == "end":
        # drawNodeF(pos, "F")


def drawStr(pos, text):
    printStr = myFont.render(str(text), False, (0, 0, 0))
    strWidth, strHeight = myFont.size(str(text))

    x = int(pos[0] - (strWidth / 2))
    y = int(pos[1] - (strHeight / 2))

    screen.blit(printStr, (x, y))


def clickController(pos):
    global timeStart
    global lastTime

    relativeMouse = ((pos[0] // sqSide) * sqSide, (pos[1] // sqSide) * sqSide)

    strWidth, strHeight = myFont.size(str("Start"))
    minX = int(resetBoxPos[0] - (strWidth / 2)) - 4
    minY = int(resetBoxPos[1] - (strHeight / 2)) - 4

    maxX = int(resetBoxPos[0] + (strWidth / 2)) + 4
    maxY = int(resetBoxPos[1] + (strHeight / 2)) + 4

    if relativeMouse in [cords for cords in playField.keys()] and gameRunning:
        updateAround(relativeMouse)

    # Start/Reset button checking cords
    elif minX < pos[0] < maxX and minY < pos[1] < maxY:
        if not gameRunning:
            timeStart = datetime.now().strftime("%H:%M:%S")
            lastTime = timeStart
        changeGS()


def updateAround(pos):
    aList = getAround(pos)

    for ite, cords in enumerate(aList):

        if cords is not None:

            # if getNodeItem(cords, "state") == "end":
            # changeGS()

            if getNodeItem(cords, "state") not in ("wall", "start", "end"):

                if ite < 4:
                    disValue = 14

                elif ite > 3:
                    disValue = 10

                oriG = getNodeItem(pos, "g")

                nodeG = oriG + disValue
                nodeH = calcNodeNum(cords, getPosByStateValue("state", "end"))
                nodeF = nodeG + nodeH

                if nodeG < getNodeItem(cords, "g"):
                    updateNodeItem(cords, "g", nodeG)

                if nodeH < getNodeItem(cords, "h"):
                    updateNodeItem(cords, "h", nodeH)

                if nodeF < getNodeItem(cords, "f"):
                    updateNodeItem(cords, "f", nodeF)
                    updateNodeItem(cords, "parent", pos)

                if getNodeItem(cords, "state") != "closed":
                    updateNodeItem(cords, "state", "open")

    if getNodeItem(pos, "state") not in ("start", "end", "wall"):
        updateNodeItem(pos, "state", "closed")


def getAround(pos):
    sideMin = 0
    topMin = 64
    sideMax = (fieldSize * sqSide) - sqSide
    botMax = fieldSize * sqSide

    xPos = pos[0]
    yPos = pos[1]

    # Top left coordinates
    if sideMin != pos[0] and topMin != pos[1]:
        tl = (xPos - sqSide, yPos - sqSide)
    else:
        tl = None

    # Top right coordinates
    if sideMax != xPos and topMin != yPos:
        tr = (xPos + sqSide, yPos - sqSide)
    else:
        tr = None

    # Bottom left coordinates
    if sideMin != xPos and botMax != yPos:
        bl = (xPos - sqSide, yPos + sqSide)
    else:
        bl = None

    # Bottom right coordinates
    if sideMax != pos[0] and botMax != pos[1]:
        br = (xPos + sqSide, yPos + sqSide)
    else:
        br = None

    # Top middle coordinates
    if topMin != yPos:
        tm = (xPos, yPos - sqSide)
    else:
        tm = None

    # Left coordinates
    if sideMin != xPos:
        left = (xPos - sqSide, yPos)
    else:
        left = None

    # Right coordinates
    if sideMax != xPos:
        right = (xPos + sqSide, yPos)
    else:
        right = None

    # Bottom middle coordinates
    if botMax != yPos:
        bm = (xPos, yPos + sqSide)
    else:
        bm = None

    return tl, tr, bl, br, tm, left, right, bm


def getNodeItem(pos, item):
    return playField[pos][item]


def calcNodeNum(pos, endPos):
    dX = abs(pos[0] - endPos[0]) / sqSide
    dY = abs(pos[1] - endPos[1]) / sqSide

    if dX > dY:
        return int(14 * dY + (10 * (dX - dY)))

    return int(14 * dX + (10 * (dY - dX)))


def getPosByStateValue(item, value):
    for pos, items in playField.items():
        if items[item] == value:
            return pos


def updateNodeItem(pos, item, value):
    playField[pos][item] = value


def changeGS():
    global gameRunning

    if gameRunning:
        gameRunning = False

    else:
        gameRunning = True


def drawBox(pos, text):
    strWidth, strHeight = myFont.size(str(text))

    x = int(pos[0] - (strWidth / 2))
    y = int(pos[1] - (strHeight / 2))

    pygame.draw.rect(screen, (0, 0, 0,), pygame.Rect(x - 4, y - 4, strWidth + 4, strHeight + 4), 2)


def drawTopBar():
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(2, 2, 636, 61))

    drawStr(timeBoxPos, "Game Time: "+str(sec))

    if gameRunning:
        drawBox(resetBoxPos, "Reset")
        drawStr(resetBoxPos, "Reset")

    else:
        drawBox(resetBoxPos, "Start")
        drawStr(resetBoxPos, "Start")


def getColorByState(state):
    if state == "start":
        return 25, 121, 169
    elif state == "end":
        return 68, 188, 216
    elif state == "wall":
        return 128, 57, 30
    elif state == "open":
        return 237, 184, 121
    elif state == "closed":
        return 224, 123, 57
    elif state == "None":
        return 255, 255, 255
    elif state == "path":
        return 0, 255, 0


def drawGame():
    drawField()
    drawTopBar()


def setStartEnd():
    updateNodeItem((0, 64), "state", "start")
    updateNodeItem((0, 64), "g", 0)
    updateNodeItem((576, 640), "state", "end")
    updateAround((0, 64))


"""
def getRandomMap():
    #set of predetermines starts and ends
    #generate random walls
    #check path is avaiable checkPath()
    #return playField
    pass

"""


def checkPath():
    # idk,
    try:
        currentNode = getPosByStateValue("state", "end")
        start = getPosByStateValue("state", "start")

        while start != currentNode:
            currentNode = getNodeItem(currentNode, "parent")
            if currentNode != start:
                updateNodeItem(currentNode, "state", "path")

        return True

    except TypeError:
        return False


def timeTicking():
    global timeStart
    global lastTime
    global sec

    new = datetime.now()
    newTime = new.strftime("%H:%M:%S")

    if newTime != lastTime:
        sec = int(newTime[6:8]) - int(timeStart[6:8]) + (int(newTime[3:5]) - int(timeStart[3:5])) * 60
        lastTime = newTime


playField = initialGen()
setStartEnd()

while gameActiveBool:

    drawGame()
    if gameRunning:
        timeTicking()

    mousePos = pygame.mouse.get_pos()

    for ev in pygame.event.get():

        # Ending game loop
        if ev.type == pygame.QUIT:
            gameActiveBool = False
            # pygame.quit()

        if ev.type == pygame.MOUSEBUTTONDOWN:
            clickController(mousePos)

    pygame.display.update()

pygame.quit()
