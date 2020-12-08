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
        # should return true if field has len path between min max

    def genRandMap(self):
        startCount = 1
        endCount = 1
        totalCount = startCount + endCount + self.wallCount

        spotDic = {}
        spotCount = -1

        for x in range(self.fieldSize):
            for y in range(self.fieldSize):
                self.field[(x, y)] = {}
                # {"f": math.inf, "g": math.inf, "h": math.inf,"state": "None","parent": tuple}

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

                if self.field[cords] == {} or self.field[cords]["state"] in ("open", "closed"):

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

                    if self.field[cords] == {} or nodeF < self.getNodeItem(cords, "f"):
                        self.updateNodeValue(cords, "g", nodeG)
                        self.updateNodeValue(cords, "h", nodeH)
                        self.updateNodeValue(cords, "f", nodeF)
                        self.updateNodeValue(cords, "parent", position)

                elif self.field[cords]["state"] == "end":
                    self.endBoolFound = True
                    self.updateNodeValue(cords, "parent", position)

                elif self.field[cords]["state"] == "unseenWall":
                    self.field[cords]["state"] = "seenWall"

        if self.field[position] == {} or self.getNodeItem(position, "state") == "open":
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


field = PlayField(10, 40, 10, 20)
field.validField()

field.updateAround(field.getPosByStateValue("state", "start"))

for key, value in field.field.items():
    if value != {}:
        print(key, value)