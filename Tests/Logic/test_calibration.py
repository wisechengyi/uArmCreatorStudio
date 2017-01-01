import unittest

from pants.util.contextutil import temporary_file, temporary_dir
from twitter.common.dirutil import safe_mkdir

from Logic.Environment import Environment


class TestCalibration(unittest.TestCase):

  def test_calibration(self):
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
