import pygame
import math
import time
import copy
from datetime import datetime
from random import randrange

pygame.init()
pygame.display.set_caption('visualApath')

sqSide = 64
fieldSize = 10

topBar = sqSide
timeBoxPos = (160, 33)
resetBoxPos = (320, 33)
stepsBoxPos = (480, 33)

res = (sqSide * fieldSize, (sqSide * fieldSize) + topBar)

screen = pygame.display.set_mode(res)
myFont = pygame.font.SysFont("Calibri", int(sqSide / 2))

gameActiveBool = True
gameRunning = False
foundEndBool = False

timeStart = 0
lastTime = 0
sec = 0
steps = 0


def drawField():
    for pos, items in playField.items():

        if items["f"] not in (math.inf, 0) and items["state"] in ("open", "closed"):
            pygame.draw.rect(screen, getColorByState(items["state"]),
                             (pos[0] + 1, (pos[1] + 1), sqSide - 2, sqSide - 2))

            drawStr(((pos[0] + (sqSide / 2)), (pos[1] + (sqSide / 2))), items["f"])

        elif items["state"] == "start":
            pygame.draw.rect(screen, getColorByState(items["state"]),
                             (pos[0] + 1, (pos[1] + 1), sqSide - 2, sqSide - 2))
            drawStr(((pos[0] + (sqSide / 2)), (pos[1] + (sqSide / 2))), "S")

        elif items["state"] == "end" and foundEndBool:
            pygame.draw.rect(screen, getColorByState(items["state"]),
                             (pos[0] + 1, (pos[1] + 1), sqSide - 2, sqSide - 2))
            drawStr(((pos[0] + (sqSide / 2)), (pos[1] + (sqSide / 2))), "f")

        elif items["state"] == "seenWall":
            pygame.draw.rect(screen, getColorByState(items["state"]),
                             (pos[0] + 1, (pos[1] + 1), sqSide - 2, sqSide - 2))


def drawStr(pos, text, color=(0, 0, 0)):
    printStr = myFont.render(str(text), False, color)
    strWidth, strHeight = myFont.size(str(text))

    x = int(pos[0] - (strWidth / 2))
    y = int(pos[1] - (strHeight / 2))

    screen.blit(printStr, (x, y))


def clickController(pos):
    global timeStart
    global lastTime
    global steps

    relativeMouse = ((pos[0] // sqSide) * sqSide, (pos[1] // sqSide) * sqSide)

    strWidth, strHeight = myFont.size(str("Start"))
    minX = int(resetBoxPos[0] - (strWidth / 2)) - 4
    minY = int(resetBoxPos[1] - (strHeight / 2)) - 4

    maxX = int(resetBoxPos[0] + (strWidth / 2)) + 4
    maxY = int(resetBoxPos[1] + (strHeight / 2)) + 4

    if relativeMouse in [cords for cords in playField.keys()] and gameRunning:
        if getNodeItem(relativeMouse, "state") == "open":
            updateAround(relativeMouse)
            steps += 1

    # Start/Reset button checking cords
    elif minX < pos[0] < maxX and minY < pos[1] < maxY:

        if not gameRunning:
            getField()

            timeStart = datetime.now().strftime("%H:%M:%S")
            lastTime = timeStart

        changeGS()
        steps = 0


def updateAround(pos):
    global foundEndBool

    aList = getAround(pos)

    for ite, cords in enumerate(aList):

        if cords is not None:

            if getNodeItem(cords, "state") == "end":
                foundEndBool = True
                updateNodeItem(cords, "parent", pos)
                if gameRunning:
                    changeGS()

            elif getNodeItem(cords, "state") == "unseenWall":
                updateNodeItem(cords, "state", "seenWall")

            if getNodeItem(cords, "state") not in ("unseenWall", "seenWall", "start", "end"):

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

    if getNodeItem(pos, "state") not in ("start", "end", "unseenWall", "seenWall"):
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

    pygame.draw.rect(screen, (255, 255, 255,), pygame.Rect(x - 4, y - 4, strWidth + 4, strHeight + 4), 2)


def drawTopBar():
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, 0, 640, 64))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(1, 1, 638, 62))

    drawStr(timeBoxPos, "Time: " + str(sec) + "s", (255, 255, 255))

    if steps == 1:
        drawStr(stepsBoxPos, "Step: " + str(steps), (255, 255, 255))
    else:
        drawStr(stepsBoxPos, "Steps: " + str(steps), (255, 255, 255))

    if gameRunning:
        drawBox(resetBoxPos, "Reset")
        drawStr(resetBoxPos, "Reset", (255, 255, 255))

    else:
        drawBox(resetBoxPos, "Start")
        drawStr(resetBoxPos, "Start", (255, 255, 255))


def getColorByState(state):
    if state == "start":
        return 25, 121, 169
    elif state == "end":
        return 68, 188, 216
    elif state == "seenWall":
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
    screen.fill((0, 0, 0))

    drawField()
    drawTopBar()


def getField():
    global playField

    playField = {}

    playField = genRandMap()
    tempField = copy.deepcopy(playField)

    setStartEnd()

    while runApath(10, 20):
        playField = genRandMap()
        tempField = copy.deepcopy(playField)

        setStartEnd()

    playField = tempField
    setStartEnd()


def setStartEnd():
    global foundEndBool
    foundEndBool = False

    updateNodeItem(getPosByStateValue("state", "start"), "g", 0)
    updateNodeItem(getPosByStateValue("state", "end"), "h", 0)
    updateAround(getPosByStateValue("state", "start"))


def genRandMap():
    startCount = 1
    endCount = 1
    wallCount = 40
    totalCount = startCount + endCount + wallCount

    fieldDic = {}
    spotDic = {}
    spotCount = 0

    for x in range(fieldSize):
        for y in range(fieldSize):
            fieldDic[(x * sqSide, topBar + (y * sqSide))] = {"f": math.inf, "g": math.inf, "h": math.inf,
                                                             "state": "None",
                                                             "parent": tuple}
            spotCount += 1
            spotDic[spotCount] = (x * sqSide, topBar + (y * sqSide))

    while totalCount > 0:
        totalCount = startCount + endCount + wallCount

        randNum = randrange(1, spotCount + 1)

        while randNum not in spotDic:
            randNum = randrange(1, spotCount + 1)

        if startCount == 1:
            fieldDic[spotDic[randNum]]["state"] = "start"
            spotDic.pop(randNum)
            startCount = 0

        elif endCount == 1:
            fieldDic[spotDic[randNum]]["state"] = "end"
            spotDic.pop(randNum)
            endCount = 0

        else:
            fieldDic[spotDic[randNum]]["state"] = "unseenWall"
            spotDic.pop(randNum)
            wallCount -= 1

    return fieldDic


def runApath(minPath, maxPath):
    try:
        while not foundEndBool:
            updateAround(getLowestFNode(playField))

        pathLen = 0
        currentNode = getPosByStateValue("state", "end")
        start = getPosByStateValue("state", "start")

        while start != currentNode:
            currentNode = getNodeItem(currentNode, "parent")
            if start != currentNode:
                updateNodeItem(currentNode, "state", "path")
                pathLen += 1

        if minPath < pathLen < maxPath:
            return False
        else:
            return True

    except TypeError:
        return True


def getLowestFNode(field):
    tempF = math.inf
    nodePos = tuple

    for pos, items in field.items():
        if items["state"] == "open":
            if items["f"] < tempF:
                tempF = items["f"]
                nodePos = pos

    return nodePos


def timeTicking():
    global timeStart
    global lastTime
    global sec

    new = datetime.now()
    newTime = new.strftime("%H:%M:%S")

    if newTime != lastTime:
        sec = int(newTime[6:8]) - int(timeStart[6:8]) + (int(newTime[3:5]) - int(timeStart[3:5])) * 60
        lastTime = newTime


playField = {}

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
