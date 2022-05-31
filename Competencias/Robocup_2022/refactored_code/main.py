import cv2 as cv
import numpy as np
import time
import copy

from data_processing import data_extractor, fixture_detection, camera_processing
import utilities, state_machines, robot, mapping

# World constants
TIME_STEP = 32
TILE_SIZE = 0.06
TIME_IN_ROUND = (8 * 60)

# Components
robot = robot.RobotLayer(TIME_STEP)

# Stores, changes and compare states
stateManager = state_machines.StateManager("init")

# Resets flags that need to be in a certain value when changing sequence, for example when changing state
def resetSequenceFlags():
    robot.delayFirstTime = True

# Sequence manager
seq = state_machines.SequenceManager(resetFunction=resetSequenceFlags)

# sequential functions used frequently
seqPrint = seq.makeSimpleEvent(print)
seqDelaySec = seq.makeComplexEvent(robot.delaySec)
seqMoveWheels = seq.makeSimpleEvent(robot.moveWheels)
seqRotateToDegs = seq.makeComplexEvent(robot.rotateToDegs)
seqMoveToCoords = seq.makeComplexEvent(robot.moveToCoords)
seqResetSequenceFlags = seq.makeSimpleEvent(resetSequenceFlags)

def isHole():
    # TODO
    return False

# Calculates offsets in the robot position, in case it doesn't start perfectly centerd
def calibratePositionOffsets():
    actualTile = [robot.position[0] // TILE_SIZE, robot.position[1] // TILE_SIZE]
    robot.positionOffsets = [
        round((actualTile[0] * TILE_SIZE) - robot.position[0]) + TILE_SIZE // 2,
        round((actualTile[1] * TILE_SIZE) - robot.position[1]) + TILE_SIZE // 2]
    robot.positionOffsets = [robot.positionOffsets[0] % TILE_SIZE, robot.positionOffsets[1] % TILE_SIZE]
    print("positionOffsets: ", robot.positionOffsets)

def seqCalibrateRobotRotation():
    # Calibrates the robot rotation using the gps
    if seq.simpleEvent():
        robot.autoDecideRotation = False
    seqMoveWheels(-1, -1)
    seqDelaySec(0.1)
    if seq.simpleEvent(): robot.rotationSensor = "gps"
    seqMoveWheels(1, 1)
    seqDelaySec(0.1)
    if seq.simpleEvent(): robot.rotationSensor= "gyro"
    seqDelaySec(0.1)
    seqMoveWheels(0, 0)
    seqMoveWheels(-1, -1)
    seqDelaySec(0.1)
    seqMoveWheels(0, 0)
    if seq.simpleEvent():
        robot.autoDecideRotation = True

doWallMapping = False
doFloorMapping = False

from data_structures import resizable_pixel_grid
lidar_grid = resizable_pixel_grid.Grid((10, 10), res=50)


# Each timeStep
while robot.doLoop():
    # Updates robot position and rotation, sensor positions, etc.
    robot.update()
    print("state: ", stateManager.state)

    # Runs once when starting the game
    if stateManager.checkState("init"):
        seq.startSequence()

        seqDelaySec(0.5)

        # Calculates offsets in the robot position, in case it doesn't start perfectly centerd
        seq.simpleEvent(calibratePositionOffsets)
            
        # Informs the mapping components of the starting position of the robot
        # seq.simpleEvent(mapping.registerStart())
        
        # Calibrates the rotation of the robot using the gps
        seqCalibrateRobotRotation()

        # Starts mapping walls
        if seq.simpleEvent():
            doWallMapping = True
            doFloorMapping = True

        # Changes state and resets the sequence
        seq.simpleEvent(stateManager.changeState, "explore")
        seq.seqResetSequence()
    
    elif stateManager.checkState("stop"):
        robot.moveWheels(0, 0)

    elif stateManager.checkState("save_img"):
        img = robot.centerCamera.getImg()
        img1 = camera_processing.flatten_image(img)
        cv.imwrite("/home/ale/rescate_laberinto/Competencias/Robocup_2022/Refactored Code/img1.png", img1)
        #stateManager.changeState("stop")
    
    elif stateManager.checkState("measure"):
        seq.startSequence()
        if seq.simpleEvent():
            initial_position = robot.position

        seqMoveToCoords((initial_position[0] + 0.12, initial_position[1] + 0.12))
        seqMoveWheels(0, 0)
        seqRotateToDegs(90)
        seqMoveWheels(0, 0)

        if seq.simpleEvent():
            start_time = time.time()

        seqRotateToDegs(270)
        #seqMoveToCoords((initial_position[0] + 0.18, initial_position[1] + 0.12))
        if seq.simpleEvent():
            print("time taken: ", time.time() - start_time)
        seqMoveWheels(0, 0)

    # Explores and maps the maze
    elif stateManager.checkState("explore"):
        seq.startSequence()
        #seqMoveWheels(0.5, -0.5)
        #seqRotateToDegs(270)

        if seq.simpleEvent():
            initial_position = robot.position

        seqMoveToCoords((initial_position[0] + 0.24, initial_position[1]))

        if seq.simpleEvent():
            initial_position = robot.position

        seqMoveToCoords((initial_position[0], initial_position[1] - 0.24))
        
        seqMoveWheels(0, 0)

        seqRotateToDegs(90)
        
        #robot.autoDecideRotation = False
        #robot.rotationSensor = "gyro"

        """
        nube_de_puntos = robot.getDetectionPointCloud()
        #print("nube de puntos: ", nube_de_puntos)
        nueva_nube_de_puntos = point_cloud_processor.processPointCloud(nube_de_puntos, robot.position)
        #print("nueva nube de puntos: ", nueva_nube_de_puntos)
        for pos in nueva_nube_de_puntos:
            round_pos = [round(pos[0] * 1000), round(pos[1]  * 1000)]
            mi_grilla.add_point(round_pos)
        mi_grilla.print_grid()
        """
        

        # lidar es robot.getLidar()
        # camaras es robot.getCameraImages()
        # grilla.update(lidar, camaras)

        # Grilla es mapping.getGrilla()
        # mejor moviemiento es AI.getMejorMovimiento(grilla)
        # coordenadas es robot.getCoordenadas(mejor movimiento)
        # robot.moveToCoords(coordenadas)
        # repetir

        imgs = (robot.rightCamera.getImg(), robot.centerCamera.getImg(), robot.leftCamera.getImg())
        data_extractor.get_floor_colors(imgs, robot.getDetectionPointCloud(), robot.rotation, robot.position)

        # If it encountered a hole
        if isHole():
            # Changes state and resets the sequence
            seq.simpleEvent(stateManager.changeState, "hole")
            seq.seqResetSequence()
        
        print("rotation:", robot.rotation)

    # What to do if it encounters a hole
    elif stateManager.checkState("hole"):
        # TODO
        pass
        # reportar obstáculo a mapping
        # moverse para atras
        # volver a "explore"
        
    # Reports a victim
    elif stateManager.checkState("report_victim"):
        seq.startSequence()
        seqDelaySec(3)
        #Classifies and reports the vicitim
        if seq.simpleEvent():
            victims = []
            for cam in (robot.leftCamera, robot.rightCamera):
                image = cam.getImg()
                vics = fixture_detection.detectVictims(image)
                victims += fixture_detection.getCloseVictims(vics)
            if len(victims) > 0:
                letter = fixture_detection.classifyFixture(victims[0])
            robot.comunicator.sendVictim(robot.position, letter)
        # TODO Reportar victima a mapping
        seq.simpleEvent(stateManager.changeState, "explore")
    
    elif stateManager.checkState("teleported"):
        seq.startSequence()
        # parar mapping
        doWallMapping = False
        seqCalibrateRobotRotation()
        # Changes state and resets the sequence
        seq.simpleEvent(stateManager.changeState, "explore")
        seq.seqResetSequence()
