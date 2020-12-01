import pygame
import math

# Initializing the constructor
pygame.init()

# Set the pygame window name
pygame.display.set_caption('visualApath')

# Square sides length
sqSide = 32
# Field sides length
fieldSize = 20

# Screen resolution
res = (sqSide * fieldSize, sqSide * fieldSize)

# Opens up a window
screen = pygame.display.set_mode(res)

# Game deactivation bool used to control game loop
gameActiveBool = True

# Game font used for rendering
myFont = pygame.font.SysFont("Comic Sans MS", 12)


# Initial generation of base field with specific parameters
def initialGen():
    global fieldSize
    global sqSide
    global gameState

    fieldDic = {}

    for x in range(fieldSize):
        for y in range(fieldSize):
            fieldDic[(x * sqSide, y * sqSide)] = {"f": math.inf, "g": math.inf, "h": math.inf, "state": "None"}

    gameState = 1

    return fieldDic


# Function for drawing the field every loop rotation
def drawField():
    for node in playField:
        x = node[0]
        y = node[1]

        if playField[node]["state"] in ("start", "end"):
            color = (0, 0, 255)

        elif playField[node]["state"] == "wall":
            color = (0, 0, 0)

        elif playField[node]["state"] == "open":
            color = (255, 0, 0)

        elif playField[node]["state"] == "closed":
            color = (0, 255, 0)

        else:
            color = (250, 250, 250)

        pygame.draw.rect(screen, color, (x + 1, y + 1, sqSide - 2, sqSide - 2))

        # Draw F here
        if playField[node]["f"] not in (math.inf, 0):
            printStr = myFont.render(str(playField[node]["f"]), False, (0, 0, 0))
            strWidth, strHeight = myFont.size(str(playField[node]["f"]))
            y = node[1] + 16
            x = node[0] + (16 - (strWidth / 2))
            posTuple = (x, y)
            screen.blit(printStr, posTuple)


# Function for changing states of the game and nodes
def changeState(pos):
    global gameState
    global wallStop
    global endPos
    global startPos

    if wallStop:
        gameState = 4

    elif gameState == 1:
        playField[pos]["state"] = "start"
        playField[pos]["g"] = 0
        gameState = 2
        startPos = pos

    elif gameState == 2 and playField[pos]["state"] != "start":
        playField[pos]["state"] = "end"
        playField[pos]["f"] = 0
        gameState = 3
        endPos = pos

    elif gameState == 3 and playField[pos]["state"] not in ("start", "end"):
        playField[pos]["state"] = "wall"

    # More states to be added in development


# Calculating coordinates of nodes around the parameters position
def around(pos):
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


def updateAround(aList, oriPos):
    for ite, cords in enumerate(aList):

        if cords is not None:

            if playField[cords]["state"] not in ("wall", "start", "end"):

                if ite < 4:
                    disValue = 14

                elif ite > 3:
                    disValue = 10

                if playField[oriPos]["g"] == math.inf:
                    oriG = 0

                else:
                    oriG = playField[oriPos]["g"]

                dX = abs(cords[0] - endPos[0]) / sqSide
                dY = abs(cords[1] - endPos[1]) / sqSide

                if dX > dY:
                    nodeH = 14 * dY + (10 * (dX - dY))
                else:
                    nodeH = 14 * dX + (10 * (dY - dX))

                if int(oriG) + disValue < playField[cords]["g"]:
                    playField[cords]["g"] = int(oriG) + disValue
                if nodeH < playField[cords]["h"]:
                    playField[cords]["h"] = int(nodeH)
                if (int(oriG) + disValue) + nodeH < playField[cords]["f"]:
                    playField[cords]["f"] = int((int(oriG) + disValue) + nodeH)

                if playField[cords]["state"] not in ("start", "end", "wall", "closed"):
                    playField[cords]["state"] = "open"
    if playField[oriPos]["state"] not in ("start", "end", "wall"):
        playField[oriPos]["state"] = "closed"


# Defining game state at 0 when the program is run
gameState = 0

# Generating initial field into a variable
playField = initialGen()

# Boolean for checking when walls should be placed
wallStop = False

# Game loop controlled by the gameActiveBool boolean
while gameActiveBool:

    drawField()

    # Stores mouse coordinates into a tuple
    mouse = pygame.mouse.get_pos()
    relativeMouse = ((mouse[0] // sqSide) * sqSide, (mouse[1] // sqSide) * sqSide)

    # Draw mouse hover square / to be removed in final product?
    pygame.draw.rect(screen, (150, 100, 0), (relativeMouse[0] + 1, relativeMouse[1] + 1, sqSide - 2, sqSide - 2))

    for ev in pygame.event.get():

        # Ending game loop
        if ev.type == pygame.QUIT:

            gameActiveBool = False
            # pygame.quit()

        elif ev.type == pygame.MOUSEBUTTONDOWN:

            # On mouse 1 press
            if ev.button == 1:

                # On mouse press 1 checking if gameState is in placement mode
                if gameState < 4:
                    # Calling changeState function with relative mouse location
                    changeState(relativeMouse)

                elif gameState == 4:
                    if playField[relativeMouse]["state"] == "open":
                        updateAround(around(relativeMouse), relativeMouse)

            # On mouse 3 press
            if ev.button == 3:

                # Checking if gameState is 3
                if gameState == 3:
                    # When mouse 3 is pressed and gameState is 3, it means no other walls are to be placed
                    wallStop = True
                    updateAround(around(startPos), startPos)

    pygame.display.update()

pygame.quit()

# to be deleted once moved to MAIN
for pos, node in playField.items():
    if node["state"] != "None":
        print(pos, node["state"])
