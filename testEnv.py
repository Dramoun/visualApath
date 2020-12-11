import math
import pygame
import copy
from random import choice
from sys import exit
from datetime import datetime


class GameRun:

    def __init__(self, sqSize, fieldSize, wallCount, pathMin, pathMax):

        # game Logic vars START
        self.sqSize = sqSize
        self.fieldSize = fieldSize
        self.wallCount = wallCount
        self.pathMin = pathMin
        self.pathMax = pathMax

        self.nodeBoarderSize = 1
        self.butBoxBorSize = 2
        self.topBarSize = sqSize
        self.timeBoxPos = (160, 33)
        self.resetBoxPos = (320, 33)
        self.stepsBoxPos = (480, 33)

        self.gameSteps = 0
        self.gameTime = 0
        self.timeStart = 0
        self.lastTime = 0

        self.gameActiveBool = True
        self.gameRunning = False
        self.gameName = 'visualApath'
        self.gameRes = (sqSize * fieldSize, (sqSize * fieldSize) + self.topBarSize)
        self.myFont = None

        self.gameScreen = pygame.display.set_mode(self.gameRes)
        # game Logic vars END

        # field Logic vars START
        self.field = {}
        self.tempField = {}
        self.endBoolFound = False
        # field Logic vars END

    # game logic functions START
    def mainLoop(self):
        pygame.init()
        pygame.display.set_caption(self.gameName)
        self.myFont = pygame.font.SysFont("Calibri", int(self.sqSize / 2))

        while self.gameActiveBool:

            self.drawGame()

            if self.gameRunning:
                self.timeTicking()

            mousePos = pygame.mouse.get_pos()

            for ev in pygame.event.get():

                if ev.type == pygame.QUIT:
                    self.gameActiveBool = False
                    pygame.quit()
                    exit(0)

                if ev.type == pygame.MOUSEBUTTONDOWN:
                    self.clickController(mousePos)

            pygame.display.update()

    def clickController(self, position):

        # Mouse click in top bar
        if position[1] < self.topBarSize:

            strWidth, strHeight = self.myFont.size(str("Start"))
            minX = int(self.resetBoxPos[0] - (strWidth / 2)) - (self.butBoxBorSize * 2)
            minY = int(self.resetBoxPos[1] - (strHeight / 2)) - (self.butBoxBorSize * 2)

            maxX = int(self.resetBoxPos[0] + (strWidth / 2)) + (self.butBoxBorSize * 2)
            maxY = int(self.resetBoxPos[1] + (strHeight / 2)) + (self.butBoxBorSize * 2)

            if minX < position[0] < maxX and minY < position[1] < maxY:

                if not self.gameRunning:
                    self.validField()

                    self.timeStart = datetime.now().strftime("%H:%M:%S")
                    self.lastTime = self.timeStart

                self.changeGS()
                self.gameSteps = 0

        # Mouse click in field
        else:
            if self.gameRunning:
                relativeMouse = (position[0] // self.sqSize,
                                 (position[1] - self.topBarSize) // self.sqSize)

                if self.getNodeItem(relativeMouse, "state") == "open":
                    self.updateAround(relativeMouse)
                    self.gameSteps += 1

    def drawGame(self):
        self.gameScreen.fill((0, 0, 0))

        self.drawField()
        self.drawTopBar()

    def drawField(self):

        for pos, items in self.field.items():

            if items["state"] not in ("unseenWall", "None"):

                drawPosX = (pos[0] * self.sqSize) + self.nodeBoarderSize
                drawPosY = (pos[1] * self.sqSize) + self.nodeBoarderSize + self.topBarSize
                drawSizeX = self.sqSize - (self.nodeBoarderSize * 2)
                drawSizeY = self.sqSize - (self.nodeBoarderSize * 2)

                if items["state"] == "end" and self.endBoolFound:
                    pygame.draw.rect(self.gameScreen, self.getColorByState(items["state"]),
                                     (drawPosX, drawPosY, drawSizeX, drawSizeY))

                elif items["state"] in ("open", "closed"):
                    pygame.draw.rect(self.gameScreen, self.getColorByState(items["state"]),
                                     (drawPosX, drawPosY, drawSizeX, drawSizeY))

                    self.drawStr((drawPosX + (self.sqSize / 2), drawPosY + (self.sqSize / 2)), items["f"])

                elif items["state"] in ("start", "seenWall"):
                    pygame.draw.rect(self.gameScreen, self.getColorByState(items["state"]),
                                     (drawPosX, drawPosY, drawSizeX, drawSizeY))

                    if items["state"] == "start":
                        # feature to be added here if we need to mark start with anything
                        pass

    def drawTopBar(self):
        pygame.draw.rect(self.gameScreen, (255, 255, 255), pygame.Rect(0, 0, 640, 64))
        pygame.draw.rect(self.gameScreen, (0, 0, 0), pygame.Rect(1, 1, 638, 62))

        self.drawStr(self.timeBoxPos, "Time: " + str(self.gameTime) + "s", (255, 255, 255))

        if self.gameSteps == 1:
            self.drawStr(self.stepsBoxPos, "Step: " + str(self.gameSteps), (255, 255, 255))
        else:
            self.drawStr(self.stepsBoxPos, "Steps: " + str(self.gameSteps), (255, 255, 255))

        if self.gameRunning:
            self.drawBox(self.resetBoxPos, "Reset")
            self.drawStr(self.resetBoxPos, "Reset", (255, 255, 255))

        else:
            self.drawBox(self.resetBoxPos, "Start")
            self.drawStr(self.resetBoxPos, "Start", (255, 255, 255))

    def drawStr(self, position, text, color=(0, 0, 0)):
        printStr = self.myFont.render(str(text), False, color)
        strWidth, strHeight = self.myFont.size(str(text))

        x = int(position[0] - (strWidth / 2))
        y = int(position[1] - (strHeight / 2))

        self.gameScreen.blit(printStr, (x, y))

    def drawBox(self, position, text):
        strWidth, strHeight = self.myFont.size(str(text))

        x = int(position[0] - (strWidth / 2)) - (self.butBoxBorSize * 2)
        y = int(position[1] - (strHeight / 2)) - (self.butBoxBorSize * 2)

        # check the boarders, should be vars not nums?
        pygame.draw.rect(self.gameScreen, (255, 255, 255,),
                         pygame.Rect(x, y, strWidth + (self.butBoxBorSize * 2), strHeight + (self.butBoxBorSize * 2)),
                         self.butBoxBorSize)

    def changeGS(self):
        if self.gameRunning:
            self.gameRunning = False

        else:
            self.gameRunning = True

    def timeTicking(self):
        new = datetime.now()
        newTime = new.strftime("%H:%M:%S")

        if newTime != self.lastTime:
            self.gameTime = int(newTime[6:8]) - int(self.timeStart[6:8]) + \
                            (int(newTime[3:5]) - int(self.timeStart[3:5])) * 60
            self.lastTime = newTime

    # game logic functions END

    # field logic functions START

    def validField(self):
        self.genRandMap()
        self.initialUpdate()
        self.tempField = copy.deepcopy(self.field)

        while self.genFieldPath():
            self.genRandMap()
            self.initialUpdate()
            self.tempField = copy.deepcopy(self.field)

        self.initialUpdate()
        self.field = self.tempField
        self.tempField = {}

    def initialUpdate(self):
        self.endBoolFound = False
        self.gameRunning = False

        self.updateNodeValue(self.getPosByStateValue("state", "start"), "g", 0)
        self.updateNodeValue(self.getPosByStateValue("state", "start"), "parent",
                             self.getPosByStateValue("state", "start"))
        self.updateNodeValue(self.getPosByStateValue("state", "end"), "h", 0)
        self.updateAround(self.getPosByStateValue("state", "start"))

    def genRandMap(self):
        walls = self.wallCount

        spotList = []

        for x in range(self.fieldSize):
            for y in range(self.fieldSize):
                self.field[(x, y)] = {"f": math.inf, "g": math.inf, "h": math.inf, "state": "None", "parent": tuple}

                spotList.append((x, y))

        startPos, endPos = self.genStartEnd()

        self.field[startPos]["state"] = "start"
        spotList.remove(startPos)

        self.field[endPos]["state"] = "end"
        spotList.remove(endPos)

        while walls > 0:
            randPos = choice(spotList)
            self.field[randPos]["state"] = "unseenWall"
            spotList.remove(randPos)
            walls -= 1

    def genFieldPath(self):
        while not self.endBoolFound:

            lowNode = self.getLowestFNode()

            if lowNode == tuple:
                return True

            else:
                self.updateAround(lowNode)

        pathLen = 0
        currentNode = self.getPosByStateValue("state", "end")
        start = self.getPosByStateValue("state", "start")

        while start != currentNode:
            currentNode = self.getNodeItem(currentNode, "parent")
            if start != currentNode:
                self.updateNodeValue(currentNode, "state", "path")
                pathLen += 1

        if self.pathMin < pathLen < self.pathMax:
            return False

        return True

    def updateAround(self, position):
        aList = self.getAround(position)

        for ite, cords in enumerate(aList):

            if cords is not None:

                if self.field[cords]["state"] in ("open", "closed", "None"):

                    if ite < 4:
                        disValue = 14

                    else:
                        disValue = 10

                    oriG = self.getNodeItem(position, "g")

                    nodeG = oriG + disValue
                    nodeH = self.calcNodeNum(cords, self.getPosByStateValue("state", "end"))
                    nodeF = nodeG + nodeH

                    if nodeF < self.getNodeItem(cords, "f"):
                        self.updateNodeValue(cords, "g", nodeG)
                        self.updateNodeValue(cords, "h", nodeH)
                        self.updateNodeValue(cords, "f", nodeF)
                        self.updateNodeValue(cords, "parent", position)

                    if self.field[cords]["state"] == "None":
                        self.updateNodeValue(cords, "state", "open")

                elif self.field[cords]["state"] == "end":
                    self.endBoolFound = True
                    self.updateNodeValue(cords, "parent", position)
                    self.changeGS()

                elif self.field[cords]["state"] == "unseenWall":
                    self.field[cords]["state"] = "seenWall"

        if self.getNodeItem(position, "state") == "open":
            self.updateNodeValue(position, "state", "closed")

    def updateNodeValue(self, position, key, value):
        self.field[position][key] = value

    def getAround(self, position):
        sideMin = 0
        sideMax = self.fieldSize - 1

        xPos = position[0]
        yPos = position[1]

        # Top left coordinates
        if sideMin not in position:
            tl = (xPos - 1, yPos - 1)
        else:
            tl = None

        # Top right coordinates
        if sideMax != xPos and sideMin != yPos:
            tr = (xPos + 1, yPos - 1)
        else:
            tr = None

        # Bottom left coordinates
        if sideMin != xPos and sideMax != yPos:
            bl = (xPos - 1, yPos + 1)
        else:
            bl = None

        # Bottom right coordinates
        if sideMax not in position:
            br = (xPos + 1, yPos + 1)
        else:
            br = None

        # Top middle coordinates
        if sideMin != yPos:
            tm = (xPos, yPos - 1)
        else:
            tm = None

        # Left coordinates
        if sideMin != xPos:
            left = (xPos - 1, yPos)
        else:
            left = None

        # Right coordinates
        if sideMax != xPos:
            right = (xPos + 1, yPos)
        else:
            right = None

        # Bottom middle coordinates
        if sideMax != yPos:
            bm = (xPos, yPos + 1)
        else:
            bm = None

        return tl, tr, bl, br, tm, left, right, bm

    def getPosByStateValue(self, item, value):
        for pos, items in self.field.items():
            if items != {} and items[item] == value:
                return pos

    def getNodeItem(self, pos, item):
        return self.field[pos][item]

    def getLowestFNode(self):
        tempF = math.inf
        nodePos = tuple

        for pos, items in self.field.items():
            if items["state"] == "open":
                if items["f"] < tempF:
                    tempF = items["f"]
                    nodePos = pos

        return nodePos

    # field logic functions END

    @staticmethod
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

    @staticmethod
    def genStartEnd():
        posChoices = (0, 1, 2, 7, 8, 9)
        endPossibility = (1, 2, 3)

        randPossibility = choice(endPossibility)

        startX = choice(posChoices)
        startY = choice(posChoices)

        if randPossibility == 1:
            if startX < 5:
                endX = startX + 7
            else:
                endX = startX - 7
            endY = startY

        elif randPossibility == 2:
            endX = startX

            if startY < 5:
                endY = startY + 7
            else:
                endY = startY - 7

        else:
            if startX < 5:
                endX = startX + 7
            else:
                endX = startX - 7

            if startY < 5:
                endY = startY + 7
            else:
                endY = startY - 7

        return (startX, startY), (endX, endY)

    @staticmethod
    def calcNodeNum(pos, endPos):
        dX = abs(pos[0] - endPos[0])
        dY = abs(pos[1] - endPos[1])

        if dX > dY:
            return int(14 * dY + (10 * (dX - dY)))

        return int(14 * dX + (10 * (dY - dX)))


GameRun(64, 10, 40, 15, 30).mainLoop()
