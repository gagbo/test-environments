
from enum import Enum
import platform
import os
import yaml
import sys

# CONFIGURE HERE ##############
node_major_version = 12
verbose_mode = False
emulator = 'Pixel_XL_API_30'
###############################

class Coin:
    def __init__(self, name):
        self.name = name
        self.config = get_product_configuration(name)

class EmptyVariable(Exception):
    pass

class OS(Enum):
    WINDOWS = 0
    MACOS = 1
    LINUX = 2

global mobile
mobile = None

global operating_system
operating_system = None

script_dir = os.path.dirname(os.path.realpath(__file__))
workdir_path = os.path.join(script_dir, '.live_sources')
cli_workdir = os.path.join(workdir_path, 'ledger-live-common', 'cli')
desktop_workdir = os.path.join(workdir_path, 'ledger-live-desktop')


# TODO: check that what is returned is not empty
def get_product_configuration(coin_name):
    with open(os.path.join(script_dir, 'config.yml'), 'r') as stream:
        try:
            sources = yaml.safe_load(stream)
        except KeyError:
            sys.stderr.write(f"Error: coin {coin_name} not found\n")
            exit(1)
        except EmptyVariable:
            sys.stderr.write(f"Error: variable has not been set for {coin_name}\n")
            exit(1)

        return sources[coin_name]['live']    