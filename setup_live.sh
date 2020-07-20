#!/bin/bash
set -e

COIN=${1}
PRODUCT='live'
SCRIPT_DIR="$(pwd)"
WORKDIR="${SCRIPT_DIR}/.${PRODUCT}_sources"

source common.sh

LIBCORE_BUILD_DIR="libcore_build"
export LEDGER_CORE_LOCAL_BUILD="${WORKDIR}/${LIBCORE_BUILD_DIR}/core/src"

LEDGER_LIVE_OPTIONS=$( get_value_from_config_file 'cli_options' )

# Prerequisite: node v12
set_node 12

# LIBCORE
retrieve_sources 'libcore'
git submodule init
git submodule update

mkdir -p ${WORKDIR}/${LIBCORE_BUILD_DIR}
cd ${WORKDIR}/${LIBCORE_BUILD_DIR}

cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTS=OFF \
    -DCMAKE_INSTALL_PREFIX=/usr/local/opt/qt5/ \
    ${WORKDIR}/lib-ledger-core

make -j${N_PROC}

# BINDINGS
retrieve_sources 'bindings'

cd ${WORKDIR}/lib-ledger-core

./tools/generateBindings.sh ${WORKDIR}/lib-ledger-core-node-bindings ${WORKDIR}/${LIBCORE_BUILD_DIR}

cd ${WORKDIR}/lib-ledger-core-node-bindings
yarn

yalc add
yalc publish

# LIVE-COMMON
retrieve_sources 'live_common'

cd ${WORKDIR}/ledger-live-common

yarn cache clean
git clean -xdf
rm -rf node_modules/

yarn install

yalc add
yalc publish

cd ${WORKDIR}/ledger-live-common/cli

yalc add @ledgerhq/ledger-core
yalc add @ledgerhq/live-common

yarn install
yarn link
yarn build

alias_command="${LEDGER_LIVE_OPTIONS} node ${WORKDIR}/ledger-live-common/cli/bin/index.js"

alias ledger-live="${alias_command}"

echo "alias ledger-live=${alias_command}"
