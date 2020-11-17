import yaml
import sys 
import os
import platform
import shutil
from pathlib import Path

script_dir = os.path.dirname(__file__)

class EmptyVariable(Exception):
    pass

# TODO: check that what is returned is not empty
def get_product_configuration(coin, product):
    with open(os.path.join(script_dir, 'config.yml'), 'r') as stream:
        try:
            sources = yaml.safe_load(stream)
        except KeyError as e:
            sys.stderr.write(f"Error: coin {coin} not found\n")
            exit(1)
        except EmptyVariable:
            sys.stderr.write(f"Error: variable has not been set for {coin} ([{product}])\n")
            exit(1)

    return sources[coin][product]


coin = sys.argv[1].lower()
print(get_product_configuration(coin, 'live'))

# Clear cache
def clear_cache():
    os = platform.system()
    home = str(Path.home())

    if os == 'Darwin':
        cache_folders = [home + '/.yalc', home + '/.yarn', home + '/.npm']

    data = input("Do you want to clear the cache?\n(" + ', '.join(cache_folders) + ' will be removed)\nyN\n')
    if data.lower() != 'y':
        return

    for cache in cache_folders:
        shutil.rmtree(cache, ignore_errors=True)


clear_cache()