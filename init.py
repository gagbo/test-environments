from helpers import *
from settings import *
import sys

def check_tooling():
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


def clear_cache():
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
            r'\AppData\Roaming\npm-cache'
            ]
    else:
        return   

    data = input("Do you want to clear the cache?\n(" + ', '.join(cache_folders) + ' will be cleared)\nyN ')
    if data.lower() != 'y':
        return

    for cache in cache_folders:
        remove_dir(home + cache)

    if mobile is not None:
        remove_dir('/tmp/metro-*')

def set_operating_system():
    if platform.system() == "Windows":
        operating_system = OS.WINDOWS
    elif platform.system() == "Darwin":
        operating_system = OS.MACOS
    else:
        operating_system = OS.LINUX

"""
Ensure that the prerequisites are met
"""
def init(coin_name):
    colorama.init() # fix git bash colored stdout issues
    check_tooling()
    check_node_version(node_major_version)
    create_workdir()
    clear_cache()
    