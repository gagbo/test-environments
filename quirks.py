import os
import fileinput
from settings import operating_system, OS

"""
Fix package.json to make it compatible with Windows
"""
def fix_package(path):
    if operating_system == OS.WINDOWS:
        package_file = os.path.join(path, 'package.json')
        for line in fileinput.input(package_file, inplace=True):
            # ./scripts/... -> bash ./scripts/...
            # '.js,.ts' -> .js,.ts
            print(line.replace("./scripts/", "bash ./scripts/").replace("'.js,.ts'", ".js,.ts"), end='')