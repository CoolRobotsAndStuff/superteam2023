current_Xcoord = 0
current_Ycoord = 0
previous_Xcoord = 0
previous_Ycoord = 0

meanX = 0
meanY = 0

direction = "right"

next_tile = (0, 0)
left_tile = (0, 0)
right_tile = (0, 0)



def update_coords (meanX, meanY):
    global current_Xcoord
    global current_Ycoord
    global previous_Xcoord
    global previous_Ycoord
    current_Xcoord = round(gps.getValues()[0]/tilesize, 1)
    current_Ycoord = round(gps.getValues()[2]/tilesize, 1)
    if abs(meanX) > 0.2:
        previous_Xcoord = current_Xcoord
    if abs(meanY) > 0.2:
        previous_Ycoord = current_Ycoord

def get_direction (meanX, meanY):
    global direction
    if abs(meanX) > abs(meanY):
        if meanX > 0:
            direction = "right"
        else:
            direction = "left"
    else:
        if meanY > 0:
            direction = "up"
        else:
            direction = "down"

def get_tiles (direction, current_Xcoord, current_Ycoord):
    global next_tile
    global left_tile
    global right_tile
    if direction == "up":
        next_tile = (current_Xcoord, current_Ycoord + 0.7)
        left_tile = (current_Xcoord - 0.7, current_Ycoord)
        right_tile = (current_Xcoord + 0.7, current_Ycoord)
    if direction == "down":
        next_tile = (current_Xcoord, current_Ycoord - 0.7)
        left_tile = (current_Xcoord + 0.7, current_Ycoord)
        right_tile = (current_Xcoord - 0.7, current_Ycoord)
    if direction == "left":
        next_tile = (current_Xcoord, current_Ycoord - 0.7)
        left_tile = (current_Xcoord - 0.7, current_Ycoord)
        right_tile = (current_Xcoord + 0.7, current_Ycoord)
    if direction == "right":
        next_tile = (current_Xcoord, current_Ycoord + 0.7)
        left_tile = (current_Xcoord + 0.7, current_Ycoord)
        right_tile = (current_Xcoord - 0.7, current_Ycoord)


while (robot.step(timeStep) != -1):

    meanX = current_Xcoord - previous_Xcoord
    meanY = current_Ycoord - previous_Ycoord

    update_coords(meanX, meanY)
    get_direction (meanX, meanY)
    get_tiles (direction, current_Xcoord, current_Ycoord)

    