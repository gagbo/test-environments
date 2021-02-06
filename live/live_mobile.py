import os
import psutil
import wget
import platform
import ssl
from zipfile import ZipFile, ZipInfo

from live.helpers import clone, run, colored
from live.settings import emulator, workdir_path

mobile_workdir = os.path.join(workdir_path, 'ledger-live-mobile')

class MyZipFile(ZipFile):
    def _extract_member(self, member, targetpath, pwd):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        targetpath = super()._extract_member(member, targetpath, pwd)

        attr = member.external_attr >> 16
        if attr != 0:
            os.chmod(targetpath, attr)
        return targetpath

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

    # if not os.path.isdir('platform-tools') or not os.path.isdir('tools'):
    #     ssl._create_default_https_context = ssl._create_unverified_context

    #     filename = wget.download("https://dl.google.com/android/repository/platform-tools-latest-" + platform.system().lower() + ".zip")
    #     MyZipFile(filename).extractall()
    #     filename = wget.download("https://dl.google.com/android/repository/sdk-tools-" + platform.system().lower() + "-4333796.zip")
    #     MyZipFile(filename).extractall()

    # os.environ['PATH'] += ":" + os.getcwd() + "/platform-tools"
    # os.environ['PATH'] += ":" + os.getcwd() + "/tools"
    # print(os.environ['PATH'])

    prepare_mobile(coin)
    
    print(colored('Run Android', 'blue'))

    run('adb start-server', cwd=mobile_workdir, background=True)
    run(f"emulator -no-snapshot -wipe-data -avd {emulator}", cwd=mobile_workdir, background=True)

    run('yarn --verbose run android', cwd=mobile_workdir)

def build_ios(coin):
    prepare_mobile(coin)

    print(colored('Run iOS', 'blue'))

    run('yarn run ios', cwd=mobile_workdir)