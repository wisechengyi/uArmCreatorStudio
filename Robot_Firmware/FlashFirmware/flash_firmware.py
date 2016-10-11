import os,io
import platform,subprocess
from serial.tools import list_ports
import requests
from tqdm import tqdm
import json


import sys
if sys.version > '3':
    PY3 = True
else:
    PY3 = False

class NetworkError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return repr(self.error)

firmware_defaul_filename = 'firmware.hex'
firmware_download_url = "http://download.ufactory.cc/firmware.hex"


class FlashFirmware:

    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        elif __file__:
            self.application_path = os.path.dirname(__file__)

        config_path = os.path.join(self.application_path, 'config.json')
        with io.open(config_path, "r", encoding="utf-8") as data_file:
            config = json.load(data_file)

        if PY3:
            self.firmware_path = os.path.join(self.application_path, config['filename'])
        else:
            self.firmware_path = os.path.join(self.application_path, config['filename'].decode("utf8").encode("latin-1"))
        self.hardware_id = config['hardware_id']
        self.firmware_url = config['download_url']
        self.download_flag = config['download_flag']

    def uarm_ports(self):
        uarm_ports = []
        for i in list_ports.comports():
            if i.hwid[0:len(self.hardware_id)] == self.hardware_id:
                uarm_ports.append(i[0])
        return uarm_ports

    def get_uarm_port_cli(self):
        uarm_list = self.uarm_ports()
        ports = self.uarm_ports()
        if len(ports) > 1:
            i = 1
            for port in ports:
                print(("[{}] - {}".format(i, port)))
                i += 1
            port_index = input("Please Choose the uArm Port: ")
            uarm_port = ports[int(port_index) - 1]
            return uarm_port
        elif len(ports) == 1:
            return uarm_list[0]
        elif len(ports) == 0:
            print ("No uArm ports is found.")
            return None

    def flash_firmware(self):
        port = self.get_uarm_port_cli()
        if port:
            global avrdude_path, error_description, cmd
            port_conf = '-P' + port
            if platform.system() == 'Darwin':
                cmd = ['avrdude', '-v', '-patmega328p', '-carduino', port_conf, '-b115200', '-D',
                       '-Uflash:w:{0}:i'.format(self.firmware_path)]
                error_description = "avrdude is required, Trying to install avrdude..."

            elif platform.system() == 'Windows':
                exe_name = 'avrdude.exe'
                conf_name = 'avrdude.conf'
                avrdude_path = os.path.join(self.application_path, 'avrdude', exe_name)
                avrdude_conf = os.path.join(self.application_path, 'avrdude', conf_name)
                cmd = [avrdude_path, '-C' + avrdude_conf, '-v', '-patmega328p', '-carduino', port_conf, '-b115200', '-D',
                       '-Uflash:w:{0}:i'.format(self.firmware_path)]
                error_description = "avrdude is required, Please try install avrdude."

            elif platform.system() == 'Linux':
                cmd = ['avrdude', '-v', '-patmega328p', '-carduino', port_conf, '-b115200', '-D',
                       '-Uflash:w:{0}:i'.format(self.firmware_path)]
                error_description = "avrdude is required, Trying to install avrdude"

            print((' '.join(cmd)))
            try:
                subprocess.call(cmd)
            except OSError as e:
                print(("Error occurred: error code {0}, error msg: {1}".format(str(e.errno), e.strerror)))
                if e.errno == 2:
                    if platform.system() == 'Darwin':
                        try:
                            print ("Installing avrdude...")
                            subprocess.call(['brew', 'install', 'avrdude'])
                            subprocess.call(cmd)
                        except OSError as e:
                            print(("Error occurred: error code {0}, error msg: {1}".format(str(e.errno), e.strerror)))
                            if e.errno == 2:
                                print ("-------------------------------------------------------")
                                print ("You didn't install homebrew, please visit http://bew.sh")
                                print ("-------------------------------------------------------")
                    if platform.system() == 'Linux':
                        print ("------------------------------------------------------------------------------")
                        print ("You didn't install avrdude.\n "
                               "please try `sudo apt-get install avrdude` or other package management command ")
                        print ("------------------------------------------------------------------------------")


    def download_firmware(self):
        print ("Downloading firmware.hex...")
        try:
            response = requests.get(self.firmware_url, stream=True)
            firmware_size = int(response.headers['content-length'])
            with open(self.firmware_path, "wb") as handle:
                for data in tqdm(response.iter_content(), total=firmware_size):
                    handle.write(data)
        except requests.exceptions.ConnectionError:
            raise NetworkError("NetWork Error, Please retry...")


def exit_fun():
    input("\nPress Enter to Exit...")


def main():
    flash = FlashFirmware()
    print (flash.firmware_path)

    if flash.download_flag:
        flash.download_firmware()
    if not os.path.exists(flash.firmware_path):
        print("firmware.hex not existed")
        exit_fun()
    else:
        flash.flash_firmware()
        exit_fun()

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        exit_fun()


