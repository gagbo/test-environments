from termcolor import colored
import colorama
import os

from live.helpers import clone, run
from live.settings import workdir_path, cli_workdir
from live.quirks import fix_package

def build(coin):
    print(colored(' LIVE-COMMON ', 'blue', 'on_yellow'))

    lc_workdir = os.path.join(workdir_path, 'ledger-live-common')

    clone(coin, layer='live_common', cwd=lc_workdir)

    fix_package(lc_workdir)

    for command in [
            'yarn install',
            'yalc publish --push'
        ]:
        run(command, cwd=lc_workdir)

    print(colored(' LIVE-COMMON: CLI ', 'blue', 'on_yellow'))

    run('yalc add @ledgerhq/live-common', cwd=cli_workdir)

    fix_package(cli_workdir)

    for command in [
            'yarn install',
            'yarn build'
        ]:
        run(command, cwd=cli_workdir)