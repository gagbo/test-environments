import os
import subprocess
from termcolor import colored
import colorama
import sys
from pathlib import Path
import shutil

from live.settings import *

"""
Run a system command
"""
def run(command, cwd=None, silent=False, background=False):
    if cwd is None:
        cwd = Path.home()

    shell = False
    if operating_system == OS.WINDOWS:
        shell = True

    if verbose_mode and ('yarn install' in command or 'yarn build' in command):
        command += ' --verbose'

    if not silent:
        print(colored(command, 'cyan'))

    out = []
    err = []

    p = None

    try:
        p = subprocess.Popen(
                command.split(), 
                stdout=None if background else subprocess.PIPE,
                stderr=None if background else subprocess.PIPE,
                stdin=subprocess.PIPE if background else None,
                bufsize=1,
                universal_newlines=True,
                shell=shell,
                cwd=cwd)

    except Exception as e:
        print('Command error:', e)
        sys.exit(1)

    if not background:
        for p_out in p.stdout:
            out.append(p_out)
            if not silent:
                print(p_out, end='')
            
        for p_err in p.stderr:
            err.append(p_err)
            if not silent:
                print(colored(p_err, 'red'))

        p.communicate()
        return '\n'.join(out), '\n'.join(err)

    else:
        f = open('pid.txt', 'w')
        print(p.pid, file=f)
        f.close()

def check_node_version(node_version):
    if operating_system == OS.WINDOWS:
        return

    out, _ = run('node --version', silent=True)
    if f"v{node_version}" not in out:
        print(f"Error: node version should be v{node_version}")
        print(f"Current version: {out}")
        sys.exit(1)

def remove_dir(dir_path):
    print(colored('Deleting ' + dir_path, 'yellow'), end='')
    # Prevent permission denied error
    if operating_system == OS.WINDOWS:
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


"""
Clone a repository
"""
def clone(coin, layer, cwd):
    repo = coin.config[layer]['repository']
    branch = coin.config[layer]['branch']
    
    run("git clone {}".format(repo), workdir_path)
    run("git checkout {}".format(branch), cwd)

