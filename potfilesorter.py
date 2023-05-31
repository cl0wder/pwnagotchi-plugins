import sys, os, subprocess, json, logging
import urllib.request
from shutil import copyfile

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.faces as faces
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

class potfilesorter(plugins.Plugin):
    __author__ = "Bauke Molenaar"
    __version__ = "1.0.1"
    __license__ = "MIT"
    __description__ = (
        "A plugin that will sort a potfile and output its to a usable wpa_supplicant.conf."
	)
    __name__ = 'potfilesorter'
    __help__ = """
    A plugin that will sort a potfile and output its to a usable wpa_supplicant.conf.
    """
    __dependencies__ = {
        'pip': ['scapy', 'shutil'],
    }
    __defaults__ = {
        'enabled': False,
        'potfile_source': '/home/pi/wpa-sec.founds.potfile',
        'dlurl': 'https://wpa-sec.stanev.org/?api&dl=1',
        'wpa_source': '/etc/wpa_supplicant/wpa_supplicant.conf',
    }

    # potfile_source = '/home/pi/wpa-sec.founds.potfile'
    # dlurl = 'https://wpa-sec.stanev.org/?api&dl=1'

    wpa_backup = "/tmp/wpa_supplicant.bak"
    wpa_tmp = "/tmp/wpa_supplicant.tmp"

    wificonfigstore_source = "/home/pi/WiFiConfigStore.xml"
    wificonfigstore_backup = "/tmp/wificonfigstore.bak"
    wificonfigstore_tmp = "/tmp/wificonfigstore.tmp"

    wificonfigstoresoftap_source = "/home/pi/WiFiConfigStoreSoftAp.xml"
    wificonfigstoresoftap_backup = "/tmp/wificonfigstoresoftap.bak"
    wificonfigstoresoftap_tmp = "/tmp/wificonfigstoresoftap.tmp"

    def __init__(self):
        self.epochs = 0
        self.train_epochs = 0

    def on_loaded(self):
        data_path = "/root/brain.json"
        self.load_data(data_path)

    def get_potfile(self, dlurl, potfile_source):
        print("Download your potfile from: " + dlurl)
        print('To: ' + potfile_source)
        #urllib.request.urlretrieve(dlurl, potfile_source)

    def backup_configs(self, wpa_tmp,wpa_source, wpa_backup, wificonfigstore_tmp, wificonfigstore_source, wificonfigstore_backup, wificonfigstoresoftap_tmp, wificonfigstoresoftap_source, wificonfigstoresoftap_backup):
        if os.path.exists(wpa_tmp):
            os.remove(wpa_tmp)
        else:
            print('Backing up: ' + wpa_source)
            print('To: ' + wpa_backup)
            copyfile(wpa_source, wpa_backup)
            print('Create tempfile to work with in: ' + wpa_tmp)
            copyfile(wpa_source, wpa_tmp)

        if os.path.exists(wificonfigstore_tmp):
            os.remove(wificonfigstore_tmp)
        else:
            print('Backing up: ' + wificonfigstore_source)
            print('To: ' + wpa_backup)
            copyfile(wificonfigstore_source, wificonfigstore_backup)
            print('Create tempfile to work with in: ' + wificonfigstore_tmp)
            copyfile(wificonfigstore_source, wificonfigstore_tmp)

        if os.path.exists(wificonfigstoresoftap_tmp):
            os.remove(wificonfigstoresoftap_tmp)
        else:
            print('Backing up: ' + wificonfigstoresoftap_source)
            print('To: ' + wificonfigstoresoftap_backup)
            copyfile(wificonfigstoresoftap_source, wificonfigstoresoftap_backup)
            print('Create tempfile to work with in: ' + wificonfigstoresoftap_tmp)
            copyfile(wificonfigstoresoftap_source, wificonfigstoresoftap_tmp)

    def copy_config(self, wpa_tmp,wpa_source, wificonfigstore_tmp, wificonfigstore_source, wificonfigstoresoftap_tmp, wificonfigstoresoftap_source):
        if os.path.exists(wpa_tmp):
            print('Copying new created config to: ' + wpa_source)
            copyfile(wpa_tmp, wpa_source)
            os.remove(wpa_tmp)
        else:
            print('Cannot copy: ' + wpa_tmp + ' to: ' + wpa_source)
            print('Are you ROOT?')
            exit()

        if os.path.exists(wificonfigstore_tmp):
            print('Copying new created config to: ' + wificonfigstore_source)
            copyfile(wificonfigstore_tmp, wificonfigstore_source)
            os.remove(wificonfigstore_tmp)
        else:
            print('Cannot copy: ' + wpa_tmp + ' to: ' + wpa_source)
            print('Are you ROOT?')
            exit()

        if os.path.exists(wificonfigstoresoftap_tmp):
            print('Copying new created config to: ' + wificonfigstore_source)
            copyfile(wificonfigstoresoftap_tmp, wificonfigstoresoftap_source)
            os.remove(wificonfigstoresoftap_tmp)
            exit()

    def checkwpaconfig(self, wpa_tmp, search_str):
        with open(wpa_tmp, 'r') as checklines:
            for line in checklines:
                if search_str in line:
                    print(search_str + ' is already in the file: ' + checklines.name)
                    return True
        print(search_str + ' is not found in: ' + checklines.name)
        return False

    def readpotfiledata(self, checkwpaconfig, potfile_source, wpa_tmp, wificonfigstore_tmp, wificonfigstoresoftap_tmp):
        with open(potfile_source, 'r') as checkpotfile:
            print('Reading: ' + checkpotfile.name + ' Data.')
            for line in checkpotfile:
                potfiledata = line.split(':')
                latitude = potfiledata[0].rstrip()
                longitude = potfiledata[1].rstrip()
                bssid = potfiledata[2].rstrip()
                wpapassword = potfiledata[3].rstrip()
                print('FOUND:')
                print('BSSID: ' + bssid)
                print('WpaPassword: ' + wpapassword)
                print('Latitude: ' + latitude)
                print('Longitude: ' + longitude)
                if checkwpaconfig(wpa_tmp, bssid):
                    print(bssid + ' Found, Skipping.')
                else:
                    with open(wpa_tmp, 'a+') as outputfile:
                        print('Found new network: ' + bssid)
                        print('Appending to: ' + outputfile.name)
                        outputfile.writelines('\n')
                        outputfile.writelines('network={' + '\n')
                        outputfile.writelines('  scan_ssid=1' + '\n')
                        outputfile.writelines('  ssid="' + bssid + '"\n')
                        outputfile.writelines('  psk="' + wpapassword + '"\n')
                        outputfile.writelines('}\n')
                        outputfile.writelines('\n')

                    with open(wificonfigstore_tmp, 'a+') as outputfile:
                        print('Found new network: ' + bssid)
                        print('Appending to: ' + outputfile.name)
                        outputfile.writelines('\n')
                        outputfile.writelines('network={' + '\n')
                        outputfile.writelines('  scan_ssid=1' + '\n')
                        outputfile.writelines('  ssid="' + bssid + '"\n')
                        outputfile.writelines('  psk="' + wpapassword + '"\n')
                        outputfile.writelines('}\n')
                        outputfile.writelines('\n')

                    with open(wificonfigstoresoftap_tmp, 'a+') as outputfile:
                        print('Found new network: ' + bssid)
                        print('Appending to: ' + outputfile.name)
                        outputfile.writelines('\n')
                        outputfile.writelines('network={' + '\n')
                        outputfile.writelines('  scan_ssid=1' + '\n')
                        outputfile.writelines('  ssid="' + bssid + '"\n')
                        outputfile.writelines('  psk="' + wpapassword + '"\n')
                        outputfile.writelines('}\n')
                        outputfile.writelines('\n')