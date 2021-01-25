import yaml
import sys 
import os
import platform
import shutil
from pathlib import Path
import subprocess
from termcolor import colored
from multiprocessing import Process

node_major_version = 12

emulator = 'Pixel_XL_API_30'

script_dir = os.path.dirname(os.path.realpath(__file__))
workdir_path = script_dir + '/.live_sources'
live_common_workdir_path = workdir_path + '/ledger-live-common'
live_common_CLI_workdir_path = workdir_path + '/ledger-live-common/cli'
live_desktop_workdir_path = workdir_path + '/ledger-live-desktop'
live_mobile_workdir_path = workdir_path + '/ledger-live-mobile'

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

if len(sys.argv) < 3:
    mobile = None
else:
    mobile = sys.argv[2].lower()

config = get_product_configuration(coin, 'live')

def run(command, cwd = None, quiet=False):
    if cwd is None:
        cwd = Path.home()

    shell = False
    if operating_system == "Windows":
        shell = True

    output = []
    errors = []

    with subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1,
        universal_newlines=True, cwd=cwd) as p:
        for line in p.stdout:
            if quiet == False:
                print(line, end='')
            output.append(line)
            
        for err in p.stderr:
            if quiet == False:
                print(colored(err, 'red'))
            errors.append(err)
  
    return '\n'.join(output), '\n'.join(errors)

    # try:
    #     p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=cwd, shell=shell)
    #     output, err = p.communicate()
    #     print(output)
    #     print(err)
    #     return output, err
    # except Exception as e:
    #     return None, str(e)

def run_detached(command, cwd):
    shell = False
    if operating_system == "Windows":
        shell = True

    subprocess.Popen(command.split(), universal_newlines=True, cwd=cwd, shell=True)

def check_tooling():
    tools = [
        'yarn --version',
        'yalc --version',
        'node --version',
        'bundle --version'
    ]

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
    # Prevent permission denied error
    if operating_system == "Windows":
        os.system('rmdir /q /s "{}" 2>NUL'.format(dir_path))
    else:
        shutil.rmtree(dir_path, ignore_errors=True)

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

def clone(app, path):
    repo = config[app]['repository']
    branch = config[app]['branch']

    run("git clone {}".format(repo), workdir_path)
    run("git checkout {}".format(branch), path)


prepare()

# Live-common
print(colored(' LIVE-COMMON ', 'blue', 'on_yellow'))
clone('live_common', live_common_workdir_path)
run('yarn install', live_common_workdir_path)
run('yalc publish --push', live_common_workdir_path)

# # Live-common: CLI
print(colored(' LIVE-COMMON: CLI ', 'blue', 'on_yellow'))

run('yalc add @ledgerhq/live-common', live_common_CLI_workdir_path)
run('yarn install', live_common_CLI_workdir_path)
run('yarn build', live_common_CLI_workdir_path)

# Live Desktop
print(colored(' DESKTOP ', 'blue', 'on_yellow'))

clone('live_desktop', live_desktop_workdir_path)

run('yalc add @ledgerhq/live-common', live_desktop_workdir_path)
run('yarn install', live_desktop_workdir_path)
run("yarn-deduplicate", live_desktop_workdir_path)
run('yarn install', live_desktop_workdir_path)

def yarn_mobile():
    run('yarn start', live_mobile_workdir_path)

# Mobile
if mobile is not None:
    print(colored(' MOBILE ', 'blue', 'on_yellow'))

    clone('live_mobile', live_mobile_workdir_path)

    run('yalc add @ledgerhq/live-common', live_mobile_workdir_path)
    run('bundle install', live_mobile_workdir_path) 
    run('yarn install', live_mobile_workdir_path) 
    run('yarn', live_mobile_workdir_path)

    p = Process(target=yarn_mobile)
    p.start()

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