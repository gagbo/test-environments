import os
import psutil

from live.helpers import clone, run, colored
from live.settings import emulator, workdir_path

mobile_workdir = os.path.join(workdir_path, 'ledger-live-mobile')

def prepare_mobile(coin):
    print(colored(' MOBILE ', 'blue', 'on_yellow'))

    clone(coin, 'live_mobile', mobile_workdir)

    for command in [
            'watchman watch-del-all',
            'rm -rf node_modules',
            'yalc add @ledgerhq/live-common',
            'bundle install',
            'yarn install',
            'yarn-deduplicate yarn.lock --strategy highest',
            'yarn install',
        ]:
        run(command, cwd=mobile_workdir)

    for _ in range(0, 3):
        run('yarn pod', mobile_workdir)

    run('yarn', cwd=mobile_workdir)
    f = open("pid.txt", "w+")
    pid = f.readline()
    f.close()
    if not pid.isnumeric() or not psutil.pid_exists(int(pid)):
        run('yarn start --reset-cache', cwd=mobile_workdir, background=True)


def build_android(coin):
    prepare_mobile(coin)
    
    print(colored('Run Android', 'blue'))

    run('adb start-server', cwd=mobile_workdir, background=True)
    run(f"emulator -no-snapshot -wipe-data -avd {emulator}", cwd=mobile_workdir, background=True)

    run('yarn --verbose run android', cwd=mobile_workdir)

def build_ios(coin):
    prepare_mobile(coin)

    print(colored('Run iOS', 'blue'))

    run('yarn run ios', cwd=mobile_workdir)