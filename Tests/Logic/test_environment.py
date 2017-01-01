import unittest

from pants.util.contextutil import temporary_file, temporary_dir
from twitter.common.dirutil import safe_mkdir

from Logic.Environment import Environment


class TestEnvironment(unittest.TestCase):
  SETTINGS = """\
    {
     "windowGeometry": "01d9d0cb0002000000000280000001220000056c0000033a00000280000001380000056c0000033a00000000000000000780",
     "consoleSettings": {
        "gui": false,
        "wordWrap": false,
        "interpreter": true,
        "robot": true,
        "other": true,
        "script": true,
        "serial": false,
        "vision": true
     },
     "coordCalibrations": {
        "groundPos": null,
        "failPts": null,
        "ptPairs": null
     },
     "windowState": "000000ff00000000fd000000010000000100000121000001d7fc0200000001fc0000002c000001d7000000bf01000014fa000000010200000002fb0000000e0043006f006e0073006f006c00650100000000ffffffff000000aa00fffffffb0000000c00430061006d0065007200610100000000ffffffff0000002900ffffff000001cb000001d700000004000000040000000800000008fc000000010000000200000001ffffffff0100000000ffffffff0000000000000000",
     "robotID": "/dev/cu.usbserial-AI04I0QM",
     "motionCalibrations": {
        "stationaryMovement": null,
        "activeMovement": null
     },
     "cameraID": 1,
     "lastOpenedFile": null
  }"""

  def testLoadEnvironment(self):
    with temporary_file() as settingsPath:
      with open(settingsPath.name, 'w') as f:
        f.write(self.SETTINGS)

      with temporary_dir() as cascadeDir:
        safe_mkdir(cascadeDir)

        with temporary_dir() as objectsPath:
          safe_mkdir(objectsPath)

          env = Environment(settingsPath=settingsPath.name, objectsPath=objectsPath, cascadePath=cascadeDir)
          # Close env first because otherwise if exception is thrown, it will never reach env.close()
          env.close()

          self.assertEqual(1, env.getSettings()['cameraID'])
          self.assertEqual('/dev/cu.usbserial-AI04I0QM', env.getSettings()['robotID'])
