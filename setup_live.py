import yaml
import sys 
import os
import platform
import shutil
from pathlib import Path
import subprocess

node_major_version = 12
live_workdir_path = '.live_sources'

script_dir = os.path.dirname(__file__)

class EmptyVariable(Exception):
    pass

# TODO: check that what is returned is not empty
def get_product_configuration(coin, product):
    with open(os.path.join(script_dir, 'config.yml'), 'r') as stream:
        try:
            sources = yaml.safe_load(stream)
        except KeyError:
            sys.stderr.write(f"Error: coin {coin} not found\n")
            exit(1)
        except EmptyVariable:
            sys.stderr.write(f"Error: variable has not been set for {coin} ([{product}])\n")
            exit(1)

    return sources[coin][product]


coin = sys.argv[1].lower()
print(get_product_configuration(coin, 'live'))

def run_command(command, cwd = None):

    if cwd is None:
        cwd = Path.home()
    
    try:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=cwd)
        output, err = p.communicate()
        return output, err
    except Exception as e:
        return None, str(e)

def check_tooling():
    tools = [
        ['yarn', '--version'],
        ['yalc', '--version'],
        ['node', '--version'],
    ]

    for tool in tools:
        out, err = run_command(tool)
        if out is None:
            print(f"Error: {tool[0]} does not seem to be installed on the system")
            print(err)
            sys.exit(1)
        else:
            print(f"{tool[0]}: {out.rstrip()}\t{err.rstrip()}")

def check_node_version(node_version):
    out, _ = run_command(['node', '--version'])
    if f"v{node_version}" not in out:
        print(f"Error: node version should be v{node_version}")
        print(f"Current version: {out}")
        sys.exit(1)

def create_workdir():
    if os.path.isdir(live_workdir_path):
            shutil.rmtree(live_workdir_path)
    
    try:
        os.mkdir(live_workdir_path)
    except OSError:
        print ("Creation of the workdir directory failed")
        sys.exit(1)

# Clear cache
def clear_cache():
    os = platform.system()
    home = str(Path.home())
 
    if os == 'Darwin':
        cache_folders = [
            '/.yalc', 
            '/.yarn', 
            '/.npm'
            ]
    elif os == 'Windows':
        cache_folders = [
            r'\AppData\Local\Yalc', 
            r'\AppData\Local\Yarn\cache', 
            r'\AppData\Roaming\npm-cache'
            ]

    data = input("Do you want to clear the cache?\n(" + ', '.join(cache_folders) + ' will be cleared)\nyN\n')
    if data.lower() != 'y':
        return

    for cache in cache_folders:
        shutil.rmtree(home + cache, ignore_errors=True)

def prepare():
    check_tooling()
    check_node_version(node_major_version)
    create_workdir()
    clear_cache()

def clone_live_common():
    out, err = run_command(['git', 'clone', sources[]], live_workdir_path)
    print(out)
    print(err)

config = get_product_configuration(coin)
prepare()
clone_live_common()