
from termcolor import colored
import colorama
import os
from helpers import clone, run
from settings import workdir_path, desktop_workdir

def build(coin):
    print(colored(' DESKTOP ', 'blue', 'on_yellow'))

    clone(coin, 'live_desktop', desktop_workdir)

    for command in [
            'yalc add @ledgerhq/live-common',
            'yarn install',
            'yarn-deduplicate yarn.lock --strategy highest',
            'yarn install'
        ]:
        run(command, cwd=desktop_workdir)