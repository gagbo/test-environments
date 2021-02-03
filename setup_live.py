#!/usr/bin/env python3

import sys, getopt
import os
from termcolor import *
import colorama

from helpers import *
from settings import *
from init import *

import live_common
import live_desktop
import live_mobile

global coin

# args
try:
    opts, args = getopt.getopt(sys.argv[1:],"hc:m:",["coin=","mobile="])
except getopt.GetoptError:
    print ('setup_live.py -c <coin name> [-m <ios|android>]')
    sys.exit(1)


for opt, arg in opts:
    if opt in ("-c", "--coin"):
        coin_name = arg
        print ('coin: ', coin_name)
    elif opt in ("-m", "--mobile"):
        mobile = arg

if coin_name is None:
    print('Coin is required: setup_live.py -c <coin name>')
    sys.exit(1)


init(coin_name)
coin = Coin(coin_name)

# LIVE-COMMON
live_common.build(coin)

# DESKTOP
live_desktop.build(coin)

# MOBILE
if mobile is not None:
    if mobile == 'android':
        live_mobile.build_android(coin)
    elif mobile == 'ios':
        live_mobile.build_ios(coin)

# Display info
print(colored(' Run Common-Live CLI: ', 'blue', 'on_white'))
print("node {}/bin/index.js".format(cli_workdir))
print(colored(' Run Desktop: ', 'blue', 'on_white'))
print("cd {} && yarn start".format(desktop_workdir))