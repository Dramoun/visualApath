import pygame
import math

pygame.init()
pygame.display.set_caption('visualApath')

sqSide = 64
fieldSize = 10
res = (sqSide * fieldSize, sqSide * fieldSize)

screen = pygame.display.set_mode(res)
myFont = pygame.font.SysFont("Calibri", int(sqSide/2))

gameActiveBool = True


def initialGen():
    fieldDic = {}

    for x in range(fieldSize):
        for y in range(fieldSize):
            fieldDic[(x * sqSide, y * sqSide)] = {"f": math.inf, "g": math.inf, "h": math.inf, "state": "None",
                                                  "parent": tuple}

    return fieldDic


def mouseController(butNum, mousePos):
    if butNum == 1:
        if getGameState() < 3:
            nextStage(getGameState(), mousePos)

    elif butNum == 3:
        if getGameState() == 3:
            updateAround(getPosByStateValue("state", "start"))
            upStage()

        if getGameState() == 6:
            gameReset()


def updateNodeItem(pos, item, value):
    playField[pos][item] = value


def getNodeItem(pos, item):
    return playField[pos][item]


def getPosByStateValue(item, value):
    for pos, items in playField.items():
        if items[item] == value:
            return pos


def getLowestFNode():
    tempF = math.inf
    nodePos = tuple

    for pos, items in playField.items():
        if items["state"] == "open":
            if items["f"] < tempF:
                tempF = items["f"]
                nodePos = pos

    return nodePos


def getAround(pos):
    sideMin = 0
    sideMax = (fieldSize * sqSide) - sqSide

    xPos = pos[0]
    yPos = pos[1]

    # Top left coordinates
    if sideMin not in pos:
        tl = (xPos - sqSide, yPos - sqSide)
    else:
        tl = None

    # Top right coordinates
    if sideMax != xPos and sideMin != yPos:
        tr = (xPos + sqSide, yPos - sqSide)
    else:
        tr = None

    # Bottom left coordinates
    if sideMin != xPos and sideMax != yPos:
        bl = (xPos - sqSide, yPos + sqSide)
    else:
        bl = None

    # Bottom right coordinates
    if sideMax not in pos:
        br = (xPos + sqSide, yPos + sqSide)
    else:
        br = None

    # Top middle coordinates
    if sideMin != yPos:
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
    if sideMax != yPos:
        bm = (xPos, yPos + sqSide)
    else:
        bm = None

    return tl, tr, bl, br, tm, left, right, bm


def updateAround(pos):
    aList = getAround(pos)

    for ite, cords in enumerate(aList):

        if cords is not None:

            if getNodeItem(cords, "state") not in ("wall", "start"):

                if ite < 4:
                    disValue = 14

                elif ite > 3:
                    disValue = 10

                oriG = getNodeItem(pos, "g")

                nodeG = oriG + disValue
                nodeH = calcNodeNum(cords, getPosByStateValue("state", "end"))

                if nodeH == 0:
                    upStage()

                nodeF = nodeG + nodeH

                if nodeG < getNodeItem(cords, "g"):
                    updateNodeItem(cords, "g", nodeG)

                if nodeH < getNodeItem(cords, "h"):
                    updateNodeItem(cords, "h", nodeH)

                if nodeF < getNodeItem(cords, "f"):
                    updateNodeItem(cords, "f", nodeF)
                    updateNodeItem(cords, "parent", pos)

                if getNodeItem(cords, "state") not in ("end", "closed"):
                    updateNodeItem(cords, "state", "open")

    if getNodeItem(pos, "state") not in ("start", "end", "wall"):
        updateNodeItem(pos, "state", "closed")


def calcNodeNum(pos, endPos):
    dX = abs(pos[0] - endPos[0]) / sqSide
    dY = abs(pos[1] - endPos[1]) / sqSide

    if dX > dY:
        return int(14 * dY + (10 * (dX - dY)))

    return int(14 * dX + (10 * (dY - dX)))


def nextStage(gs, pos):
    if gs == 1:
        updateNodeItem(pos, "state", "start")
        updateNodeItem(pos, "g", 0)
        upStage()

    elif gs == 2 and getNodeItem(pos, "state") != "start":
        updateNodeItem(pos, "state", "end")
        updateNodeItem(pos, "h", 0)
        upStage()

    elif gs == 3 and getNodeItem(pos, "state") not in ("start", "end", "wall"):
        updateNodeItem(pos, "state", "wall")


def upStage():
    global gameState
    gameState += 1


def getGameState():
    global gameState
    return gameState


def drawField():
    for pos, items in playField.items():
        pygame.draw.rect(screen, getColorByState(items["state"]), (pos[0] + 1, pos[1] + 1, sqSide - 2, sqSide - 2))

        if items["f"] not in (math.inf, 0) and items["state"] not in ("start", "end", "wall"):
            drawStr(pos, items["f"])

        if items["state"] == "start":
            drawStr(pos, "S")

        elif items["state"] == "end":
            drawStr(pos, "F")


def drawStr(pos, text):
    printStr = myFont.render(str(text), False, (0, 0, 0))
    strWidth, strHeight = myFont.size(str(text))
    y = int(pos[1] + (sqSide/3))
    x = int((pos[0] + ((sqSide/2) - (strWidth / 2))))
    posTuple = (x, y)
    screen.blit(printStr, posTuple)


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


def getPath():
    currentNode = getPosByStateValue("state", "end")
    start = getPosByStateValue("state", "start")

    while start != currentNode:
        currentNode = getNodeItem(currentNode, "parent")
        if currentNode != start:
            updateNodeItem(currentNode, "state", "path")

    upStage()


def gameController(gs):
    try:
        if gs == 3:
            if pygame.mouse.get_pressed(3)[0]:
                nextStage(gs, relativeMouse)

        elif gs == 4:
            updateAround(getLowestFNode())

        elif gs == 5:
            getPath()

    except TypeError:
        gameReset()


def gameReset():
    global gameState
    global playField

    playField = initialGen()
    gameState = 1


playField = initialGen()
gameState = 1

while gameActiveBool:

    drawField()

    mouse = pygame.mouse.get_pos()
    relativeMouse = ((mouse[0] // sqSide) * sqSide, (mouse[1] // sqSide) * sqSide)

    for ev in pygame.event.get():

        # Ending game loop
        if ev.type == pygame.QUIT:
            gameActiveBool = False
            # pygame.quit()

        if ev.type == pygame.MOUSEBUTTONDOWN:
            mouseController(ev.button, relativeMouse)

    gameController(getGameState())

    pygame.display.update()

pygame.quit()
