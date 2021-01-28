#!/usr/bin/python

import yaml
import sys 
import os
import platform
import shutil
import fileinput
from pathlib import Path
import subprocess
from termcolor import colored

node_major_version = 12
verbose_mode = True

emulator = 'Pixel_XL_API_30'

script_dir = os.path.dirname(os.path.realpath(__file__))
workdir_path = os.path.join(script_dir, '.live_sources')

operating_system = platform.system()

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
config = get_product_configuration(coin, 'live')

if len(sys.argv) < 3:
    mobile = None
else:
    mobile = sys.argv[2].lower()

"""
Run a system command
"""

def run(command, cwd=None, verbose=False, silent=False):
    if cwd is None:
        cwd = Path.home()

    shell = False
    if operating_system == "Windows":
        shell = True

    if verbose == True:
        command += ' --verbose'

    out = []
    err = []

    with subprocess.Popen(
            command.split(), 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            bufsize=1,
            universal_newlines=True,
            shell=shell,
            cwd=cwd) as p:

        for p_out in p.stdout:
            out.append(p_out)
            if not silent:
                print(p_out, end='')
            
        for p_err in p.stderr:
            err.append(p_err)
            if not silent:
                print(colored(p_err, 'red'))

        _, _ = p.communicate()
  
    return '\n'.join(out), '\n'.join(err)

def check_tooling():
    tools = [
        'yarn --version',
        'yalc --version',
        'node --version',
    ]

    if mobile is not None:
        tools.append('ruby --version')
        tools.append('watchman --version')
        tools.append('bundle --version')

    for tool in tools:
        print(tool, '\t', end='')
        out, err = run(tool)
        if len(out) == 0:
            print(f"Error: {tool.split()[0]} does not seem to be installed on the system")
            print(err)
            sys.exit(1)

def check_node_version(node_version):
    if operating_system == 'Windows':
        return

    out, _ = run('node --version', quiet=True)
    if f"v{node_version}" not in out:
        print(f"Error: node version should be v{node_version}")
        print(f"Current version: {out}")
        sys.exit(1)

def remove_dir(dir_path):
    print(colored('Deleting ' + dir_path, 'yellow'), end='')
    # Prevent permission denied error
    if operating_system == "Windows":
        os.system('rmdir /q /s "{}" 2>NUL'.format(dir_path))
    else:
        shutil.rmtree(dir_path, ignore_errors=True)
    print(colored(' [done]', 'yellow'))

def create_workdir():
    if os.path.isdir(workdir_path):
        remove_dir(workdir_path)
    
    try:
        os.mkdir(workdir_path)
    except OSError:
        print ("Creation of the workdir directory failed")
        sys.exit(1)

def clear_cache():
    home = str(Path.home())

    if operating_system == 'Darwin':
        cache_folders = [
            '/.yalc', 
            '/.yarn', 
            '/.npm'
            ]
    elif operating_system == 'Windows':
        cache_folders = [
            r'\AppData\Local\Yalc', 
            r'\AppData\Local\Yarn\cache', 
            r'\AppData\Roaming\npm-cache'
            ]

    data = input("Do you want to clear the cache?\n(" + ', '.join(cache_folders) + ' will be cleared)\nyN ')
    if data.lower() != 'y':
        return

    for cache in cache_folders:
        remove_dir(home + cache)

def prepare():
    check_tooling()
    check_node_version(node_major_version)
    create_workdir()
    clear_cache()

"""
Clone a repository
"""
def clone(app, path):
    repo = config[app]['repository']
    branch = config[app]['branch']

    run("git clone {}".format(repo), workdir_path)
    run("git checkout {}".format(branch), path)

"""
Fix package.json to make it compatible with Windows
"""
def fix_package(path):
    if operating_system == "Windows": 
        package_file = os.path.join(path, 'package.json')
        for line in fileinput.input(package_file, inplace=True):
            print(line.replace("./scripts/", "bash ./scripts/"), end='')
            print(line.replace("'.js,.ts'", ".js,.ts"), end='')

prepare()

# Live-common
print(colored(' LIVE-COMMON ', 'blue', 'on_yellow'))

live_common_workdir_path = os.path.join(workdir_path, 'ledger-live-common')

clone('live_common', live_common_workdir_path)

fix_package(live_common_workdir_path)

run('yarn install', live_common_workdir_path, verbose=verbose_mode)
run('yalc publish --push', live_common_workdir_path)

# # # Live-common: CLI
print(colored(' LIVE-COMMON: CLI ', 'blue', 'on_yellow'))

live_common_CLI_workdir_path = os.path.join(workdir_path, 'ledger-live-common', 'cli')

run('yalc add @ledgerhq/live-common', live_common_CLI_workdir_path)

fix_package(live_common_CLI_workdir_path)

run('yarn install', live_common_CLI_workdir_path, verbose=verbose_mode)
run('yarn build', live_common_CLI_workdir_path, verbose=verbose_mode)

# Live Desktop
print(colored(' DESKTOP ', 'blue', 'on_yellow'))

live_desktop_workdir_path = os.path.join(workdir_path, 'ledger-live-desktop')

clone('live_desktop', live_desktop_workdir_path)

run('yalc add @ledgerhq/live-common', live_desktop_workdir_path)
run('yarn install', live_desktop_workdir_path, verbose=verbose_mode)
run("yarn-deduplicate", live_desktop_workdir_path, verbose=verbose_mode)
run('yarn install', live_desktop_workdir_path, verbose=verbose_mode)

# Mobile
if mobile is not None:
    live_mobile_workdir_path = os.path.join(workdir_path, 'ledger-live-mobile')

    print(colored(' MOBILE ', 'blue', 'on_yellow'))

    clone('live_mobile', live_mobile_workdir_path)

    run('yalc add @ledgerhq/live-common', live_mobile_workdir_path)
    run('bundle install', live_mobile_workdir_path) 
    run('yarn install', live_mobile_workdir_path)

    for i in range(0, 3):
        run('yarn pod', live_mobile_workdir_path)

    run('yarn', live_mobile_workdir_path)
    run('yarn start &', live_mobile_workdir_path)

    if mobile == 'android':
        print(colored('Run Android', 'blue'))
        run('adb start-server', live_mobile_workdir_path)
        run(f"emulator -avd ${emulator}", live_mobile_workdir_path)

        run('yarn run android', live_mobile_workdir_path)

    elif mobile == 'ios':
        print(colored('Run iOS', 'blue'))
        run('yarn run ios', live_mobile_workdir_path)


# Display info
print("node {}/bin/index.js".format(live_common_CLI_workdir_path))
print("cd {} && yarn start".format(live_desktop_workdir_path))