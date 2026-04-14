import glob
from pathlib import Path

DEVICES_DIR = "/sys/bus/w1/devices/"


def find_device():
    device_folder = glob.glob(DEVICES_DIR + "28*")[0]
    device_file = device_folder + "/w1_slave"
