import math
import pygame
import copy
import random


class PlayField:

    def __init__(self, fieldSize, wallCount, pathMin, pathMax):
        self.field = {}
        self.fieldSize = fieldSize
        self.wallCount = wallCount
        self.pathMin = pathMin
        self.pathMax = pathMax

        self.endBoolFound = False
        self.tempField = {}

        self.validField()

    def validField(self):
        self.genRandMap()
        self.initialUpdate()
        self.tempField = copy.deepcopy(self.field)

        while self.genFieldPath():
            self.genRandMap()
            self.initialUpdate()
            self.tempField = copy.deepcopy(self.field)

        self.field = self.tempField

    def initialUpdate(self):
        self.endBoolFound = False

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
            randPos = random.choice(spotList)
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

    @staticmethod
    def genStartEnd():
        posChoices = (0, 1, 2, 7, 8, 9)
        endPossibility = (1, 2, 3)

        randPossibility = random.choice(endPossibility)

        startX = random.choice(posChoices)
        startY = random.choice(posChoices)

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


class GameLogic:

    def __init__(self, sqSize, fieldSize):
        self.sqSize = sqSize
        self.fieldSize = fieldSize

        self.nodeBoarderSize = 1
        self.field = PlayField(fieldSize, 40, 15, 30).field
        self.gameActiveBool = True
        self.gameName = 'visualApath'
        self.gameRes = (sqSize*fieldSize, sqSize*fieldSize)

        self.gameScreen = pygame.display.set_mode(self.gameRes)

    def initialLoad(self):
        pygame.init()
        pygame.display.set_caption(self.gameName)

    def mainLoop(self):
        self.initialLoad()

        while self.gameActiveBool:

            self.drawField()

            for ev in pygame.event.get():

                if ev.type == pygame.QUIT:

                    self.gameActiveBool = False
                    pygame.quit()

            pygame.display.update()

    def drawField(self):
        for pos, items in self.field.items():
            pygame.draw.rect(self.gameScreen, self.getColorByState(items["state"]),
                             ((pos[0] * self.sqSize) + self.nodeBoarderSize, ((pos[1] * self.sqSize) + self.nodeBoarderSize), 62, 62))

    def getColorByState(self, state):
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
        elif state == "unseenWall":
            return 128, 57, 30


run = GameLogic(64, 10)
run.mainLoop()
