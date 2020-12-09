import math
import pygame
from random import randrange


class PlayField:

    def __init__(self, fieldSize, wallCount, pathMin, pathMax):
        self.field = {}
        self.fieldSize = fieldSize
        self.wallCount = wallCount
        self.pathMin = pathMin
        self.pathMax = pathMax

        self.endBoolFound = False

    def validField(self):
        self.genRandMap()
        self.initialUpdate()

        while self.genFieldPath():
            print(1)
            self.genRandMap()
            self.initialUpdate()
        # should return true if field has len path between min max

    def genRandMap(self):
        startCount = 1
        endCount = 1
        totalCount = startCount + endCount + self.wallCount

        spotDic = {}
        spotCount = -1

        for x in range(self.fieldSize):
            for y in range(self.fieldSize):
                self.field[(x, y)] = {"f": math.inf, "g": math.inf, "h": math.inf, "state": "None", "parent": tuple}

                spotCount += 1
                spotDic[spotCount] = (x, y)

        while totalCount > 0:
            totalCount = startCount + endCount + self.wallCount

            randNum = randrange(spotCount)

            while randNum not in spotDic:
                randNum = randrange(1, spotCount + 1)

            if startCount == 1:
                self.field[spotDic[randNum]]["state"] = "start"
                spotDic.pop(randNum)
                startCount = 0

            elif endCount == 1:
                self.field[spotDic[randNum]]["state"] = "end"
                spotDic.pop(randNum)
                endCount = 0

            else:
                self.field[spotDic[randNum]]["state"] = "unseenWall"
                spotDic.pop(randNum)
                self.wallCount -= 1

    def genFieldPath(self):
        while not self.endBoolFound:
            if not self.getLowestFNode():
                return True
            else:
                self.updateAround(self.getLowestFNode())

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

    def updateAround(self, position):
        aList = self.getAround(position)

        for ite, cords in enumerate(aList):

            if cords is not None:

                if self.field[cords]["state"] in ("open", "closed", "None"):

                    if self.field[cords] != "closed":
                        self.updateNodeValue(cords, "state", "open")

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

                elif self.field[cords]["state"] == "end":
                    self.endBoolFound = True
                    self.updateNodeValue(cords, "parent", position)

                elif self.field[cords]["state"] == "unseenWall":
                    self.field[cords]["state"] = "seenWall"

        if self.getNodeItem(position, "state") == "open":
            self.updateNodeValue(position, "state", "closed")

    def initialUpdate(self):
        self.endBoolFound = False

        self.updateNodeValue(self.getPosByStateValue("state", "start"), "g", 0)
        self.updateNodeValue(self.getPosByStateValue("state", "end"), "h", 0)
        self.updateAround(self.getPosByStateValue("state", "start"))

    def updateNodeValue(self, position, key, value):
        self.field[position][key] = value

    def getPosByStateValue(self, item, value):
        for pos, items in self.field.items():
            if items != {} and items[item] == value:
                return pos

    def getNodeItem(self, pos, item):
        return self.field[pos][item]

    @staticmethod
    def calcNodeNum(pos, endPos):
        dX = abs(pos[0] - endPos[0])
        dY = abs(pos[1] - endPos[1])

        if dX > dY:
            return int(14 * dY + (10 * (dX - dY)))

        return int(14 * dX + (10 * (dY - dX)))

    def getLowestFNode(self):
        tempF = math.inf
        nodePos = tuple

        for pos, items in self.field.items():
            if items["state"] == "open":
                if items["f"] < tempF:
                    tempF = items["f"]
                    nodePos = pos

        if nodePos == tuple:
            return False

        return nodePos


field = PlayField(10, 40, 10, 20)
field.validField()


gameActiveBool = True
res = (640, 640)
screen = pygame.display.set_mode(res)
pygame.init()
pygame.display.set_caption('visualApath')

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
    elif state == "unseenWall":
        return 128, 57, 30


while gameActiveBool:

    for pos, items in field.field.items():
        pygame.draw.rect(screen, getColorByState(items["state"]),
                         ((pos[0]*64) + 1, ((pos[1]*64) + 1), 62, 62))

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            gameActiveBool = False

    pygame.display.update()

pygame.quit()
