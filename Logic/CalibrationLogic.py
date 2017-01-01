import copy
import logging
import math

from Logic.Robot import ROBOT_MARKER, OutOfBoundError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CalibrationLogic(object):
  def __init__(self, env, groundCoord):
    super(CalibrationLogic)
    self.env = env
    self.groundCoord = groundCoord

  def getPoint(self, textLabel=None, cancelTestButton=None, testRunning=None):
    errors = []
    newCalibrations = {"ptPairs": [], "failPts": []}

    def getMarkerImageCoord(physical_coord):
      # Move the robot to the coordinate
      robot.setPos(coord=physical_coord)
      vision.waitForNewFrames(3)

      # Now that the robot is at the desired position, get the avg location
      frameAge, marker = vision.getObjectLatestRecognition(rbMarker)

      # Make sure the robot is still connected before checking anything else
      if not robot.connected():
        errors.append(self.tr("Robot was disconnected during calibration"))
        return None

      # Make sure the object was found in a recent frame
      if marker is None or not frameAge < 2:
        logger.error("GUI| Marker was not recognized.")
        return None

      return marker.center



    # Get variables that will be used
    robot = self.env.getRobot()
    vision = self.env.getVision()
    rbMarker = self.env.getObjectManager().getObject(ROBOT_MARKER)

    def findViewLimit(startCoord, axis, direction):
      """
      :param start: staring coordinate
      :param axis: 0 - x, 1 - y, 2 - z
      :param direction: +/-1
      :return: the max/min value in that axis
      """
      limit = startCoord[axis]
      while True:
        try:
          robot.setPos(coord=startCoord)
        except OutOfBoundError:
          return limit

        if not getMarkerImageCoord(startCoord):
          limit = startCoord[axis]
          break
        startCoord[axis] += .5 * direction

      return limit

    # Find the limit in each axis
    start = [0, 20, float(round(self.groundCoord[2] + 2.0, 2))]
    xMax = findViewLimit(copy.copy(start), 0, 1)
    xMin = findViewLimit(copy.copy(start), 0, -1)
    yMax = findViewLimit(copy.copy(start), 1, 1)
    yMin = findViewLimit(copy.copy(start), 1, -1)

    # Generate a large set of points to test the robot, and put them in testCoords
    testCoords = []

    # Test the z on 3 xy points
    zTest = int(round(start[2], 0))  # Since range requires an integer, round zLower just for this case
    for x in range(math.ceil(xMin), math.floor(xMax), 1):
      testCoords.append([x, (yMax + yMin) / 2, zTest])  # Center of XYZ grid

    for y in range(math.ceil(yMin), math.floor(yMax), 1):
      testCoords.append([(xMax + xMin) / 2, y, zTest])

    for z in range(zTest, 19, 1):
      testCoords.append([(xMax + xMin) / 2, (yMax + yMin) / 2, z])

    for x in range(math.ceil(xMin), math.floor(xMax), 1):
      testCoords.append([x, (yMax + yMin) / 2, 17])  # Center of XY, top z

    for y in range(math.ceil(yMin), math.floor(yMax), 4):
      testCoords.append([0, y, 17])

    direction = 1
    for y in range(math.ceil(yMin), math.floor(yMax), 2):
      for x in range(math.ceil(xMin) * direction, math.floor(xMax) * direction, direction):
        testCoords.append([x, y, zTest])
      direction *= -1

    for i, coord in enumerate(testCoords):
      if cancelTestButton:
        testRunning = False
        return

      successPoints = newCalibrations["ptPairs"]
      failurePoints = newCalibrations["failPts"]

      text = "Calibration Progress:\n{}/{}, success: {}, failure: {}" \
        .format(i, len(testCoords), len(successPoints), len(failurePoints))
      if textLabel:
        textLabel.setText(text)

      markerCenter = getMarkerImageCoord(coord)

      if markerCenter:
        successPoints.append([markerCenter, coord])
      else:
        newCalibrations['failPts'].append(coord)


    return errors, newCalibrations, testCoords

