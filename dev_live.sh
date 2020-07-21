#!/bin/bash
set -e

COIN=${1}
PRODUCT='live'
SCRIPT_DIR="$(pwd)"
WORKDIR="${SCRIPT_DIR}/.${PRODUCT}_sources"

DEV_DIR="/Users/glethuillier/ledger-live-common"

LIBCORE_BUILD_DIR="libcore_build"
export LEDGER_CORE_LOCAL_BUILD="${WORKDIR}/${LIBCORE_BUILD_DIR}/core/src"

get_value_from_config_file() {
  SOURCE=$( python3 ${SCRIPT_DIR}/read_config_file.py ${COIN} ${PRODUCT} ${1} ${2} )
  exitcode=$?
  if [ ${exitcode} != 0 ]; then exit ${exitcode}; fi
  if [ -z "${SOURCE}" ]; then exit 1; fi
  echo ${SOURCE}
}

LEDGER_LIVE_OPTIONS=$( get_value_from_config_file 'options' )

# LIVE-COMMON

cd "${WORKDIR}/ledger-live-common"

# Files/directories to copy
cp -vf "${DEV_DIR}/src/families/algorand/specs.js" src/families/algorand/specs.js
cp -vf "${DEV_DIR}/src/families/algorand/speculos-deviceActions.js" src/families/algorand/speculos-deviceActions.js

yalc publish --push

alias_command="${LEDGER_LIVE_OPTIONS} node cli/bin/index.js"

alias ledger-live="${alias_command}"

echo "alias ledger-live=${alias_command}"
