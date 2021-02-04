import sys
from pathlib import Path
from termcolor import colored
import colorama
import psutil

from live.helpers import run, remove_dir, platform, check_node_version, create_workdir
from live.settings import operating_system, OS, node_major_version

def check_tooling(mobile):
    print(colored('Checking required tools...', 'yellow'))
    tools = [
        'yarn --version',
        'yalc --version',
        'node --version',
        'yarn-deduplicate --version'
    ]

    if mobile is not None:
        tools.append('ruby --version')
        tools.append('watchman --version')
        tools.append('bundle --version')

    for tool in tools:
        out, err = run(tool)
        if len(out) == 0:
            print(f"Error: {tool.split()[0]} does not seem to be installed on the system")
            print(err)
            sys.exit(1)


def clear_cache(mobile):
    home = str(Path.home())

    if operating_system in (OS.LINUX, OS.MACOS):
        cache_folders = [
            '.yalc', 
            '.yarn', 
            '.npm'
            ]
    elif operating_system == OS.WINDOWS:
        cache_folders = [
            r'\AppData\Local\Yalc', 
            r'\AppData\Local\Yarn\cache', 
            r'\AppData\Roaming\npm-cache',
            r'AppData\Roaming\Ledger Live\Cache'
            ]

    # Electron cache
    if operating_system == OS.MACOS:
        cache_folders.append('/Library/ApplicationSupport/Ledger Live/Cache')
    elif operating_system == OS.LINUX:
        cache_folders.append('.config/Ledger Live/Cache')

    data = input("Do you want to clear the cache?\n(" + ', '.join(cache_folders) + ' will be cleared)\nyN ')
    if data.lower() != 'y':
        return

    for cache in cache_folders:
        remove_dir(home + cache)

    if mobile is not None:
        remove_dir('/tmp/metro-*')    


def kill_live():
    data = input("Do you want to kill the current node processes?\nyN ")
    if data.lower() != 'y':
        return

    for proc in psutil.process_iter():
        if proc.name() == 'node':
            print(colored(f"Killing {proc}", 'yellow'))
            proc.kill()

"""
Ensure that the prerequisites are met
"""
def setup(coin_name, mobile):
    colorama.init() # fix git bash colored stdout issues
    check_tooling(mobile)
    check_node_version(node_major_version)
    create_workdir()
    clear_cache(mobile)
    kill_live()
