#!/bin/bash
set -e

COIN=${1}
LIBCORE_MODE=${2}
PRODUCT='live'
SCRIPT_DIR="$(pwd)"
WORKDIR="${SCRIPT_DIR}/.${PRODUCT}_sources"

source common.sh

LEDGER_LIVE_OPTIONS=$( get_value_from_config_file 'options' )

# Prerequisite: node v12
set_node 12

# Remove existing db
rm -rf "${SCRIPT_DIR}/dbdata" 2>/dev/null

# Remove cache
rm -rfv ~/.yalc/{*,.*} || true
rm -rfv ~/.yarn/{*,.*} || true
rm -rfv ~/.npm/{*,.*} || true

# Ensure that ledger-live is not installed globally
npm uninstall ledger-live -g
rm /usr/local/bin/ledger-live || true

# LIBCORE (Build)
if [ -n "${LIBCORE_MODE}" ] && [ "${LIBCORE_MODE}" == "build" ]; then 
    LIBCORE_BUILD_DIR="libcore_build"
    export LEDGER_CORE_LOCAL_BUILD="${WORKDIR}/${LIBCORE_BUILD_DIR}/core/src"

    retrieve_sources 'libcore'
    git submodule update --init

    mkdir -p ${WORKDIR}/${LIBCORE_BUILD_DIR}
    cd ${WORKDIR}/${LIBCORE_BUILD_DIR}

    cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_TESTS=OFF \
        ${WORKDIR}/lib-ledger-core

    make -j${N_PROC}
fi

# BINDINGS
retrieve_sources 'bindings'

if [ -n "${LIBCORE_MODE}" ] && [ "${LIBCORE_MODE}" == "build" ]; then
    cd ${WORKDIR}/lib-ledger-core
    ./tools/generateBindings.sh ${WORKDIR}/lib-ledger-core-node-bindings ${WORKDIR}/${LIBCORE_BUILD_DIR}
fi

cd ${WORKDIR}/lib-ledger-core-node-bindings

yarn cache clean

yarn install --verbose

yalc add

yalc publish --push

# LIVE-COMMON
retrieve_sources 'live_common'

cd ${WORKDIR}/ledger-live-common

yarn install --verbose

yalc add

yalc publish --push

cd ${WORKDIR}/ledger-live-common/cli

yalc add @ledgerhq/ledger-core
yalc add @ledgerhq/live-common

yarn install --verbose
yarn link --verbose
yarn build --verbose

# LIVE-DESKTOP
retrieve_sources 'live_desktop'

cd ${WORKDIR}/ledger-live-desktop

yalc add @ledgerhq/live-common
yalc add @ledgerhq/ledger-core

sed -i -- 's/5.19.0/5.19.1/g' package.json

yarn install

alias_cli_command="${LEDGER_LIVE_OPTIONS} node ${WORKDIR}/ledger-live-common/cli/bin/index.js"
alias_desktop_command="cd ${WORKDIR}/ledger-live-desktop && yarn start"

alias ledger-live="${alias_cli_command}"
alias ledger-desktop="${alias_desktop_command}"

echo "alias ledger-live=\"${alias_cli_command}\""
echo "alias ledger-desktop=\"${alias_desktop_command}\""
