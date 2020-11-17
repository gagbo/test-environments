#!/bin/bash

# Remove cache
read -p "The contents of ~/.yalc, ~/.yarn, and ~/.npm are about to be deleted. Do you want to continue? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

rm -rfv ~/.yalc/{*,.*} || true
rm -rfv ~/.yarn/{*,.*} || true
rm -rfv ~/.npm/{*,.*}  || true

COIN=${1}
LIBCORE_MODE=${2}
PRODUCT='live'
SCRIPT_DIR="$(pwd)"
WORKDIR="${SCRIPT_DIR}/.${PRODUCT}_sources"

source common.sh

LEDGER_LIVE_OPTIONS=$( get_value_from_config_file 'options' )

# Prerequisite: node v12
set_node 12 || return

# Ensure that ledger-live is not installed globally
npm uninstall ledger-live -g
rm /usr/local/bin/ledger-live || true

(
    set -e

    # LIBCORE
    if [ -n "${LIBCORE_MODE}" ]
    then
        LIBCORE_BUILD_DIR="libcore_build"
        export LEDGER_CORE_LOCAL_BUILD="${WORKDIR}/${LIBCORE_BUILD_DIR}/core/src"

        mkdir -p "${WORKDIR}/${LIBCORE_BUILD_DIR}"

        # Build
        if [ "${LIBCORE_MODE}" = "build" ]
        then
            retrieve_sources 'libcore'
            git submodule update --init

            cd "${WORKDIR}/${LIBCORE_BUILD_DIR}"

            cmake \
                -DCMAKE_BUILD_TYPE=Release \
                -DBUILD_TESTS=OFF \
                "${WORKDIR}/lib-ledger-core"

            make -j${N_PROC}
        
        # Use local file
        elif [ "${LIBCORE_MODE}" = "file" ]
        then
            FILE_PATH=${3}

            mkdir -p "${WORKDIR}/${LIBCORE_BUILD_DIR}/core/src"
            cp -fv "${FILE_PATH}" "${WORKDIR}/${LIBCORE_BUILD_DIR}/core/src"
        fi
    fi

    # BINDINGS
    #retrieve_sources 'bindings'

    #if [ -n "${LIBCORE_MODE}" ] && [ "${LIBCORE_MODE}" = "build" ]; then
    #    cd ${WORKDIR}/lib-ledger-core
    #    ./tools/generateBindings.sh ${WORKDIR}/lib-ledger-core-node-bindings ${WORKDIR}/${LIBCORE_BUILD_DIR}
    #fi

    #cd ${WORKDIR}/lib-ledger-core-node-bindings

    #yarn install

    #yalc publish --push

    # LIVE-COMMON
    retrieve_sources 'live_common'

    cd ${WORKDIR}/ledger-live-common

    yarn install

    yalc publish --push

    cd ${WORKDIR}/ledger-live-common/cli

    #yalc add @ledgerhq/ledger-core
    yalc add @ledgerhq/live-common

    yarn install
    yarn build

    npm rebuild

    # LIVE-DESKTOP
    # retrieve_sources 'live_desktop'

    # cd ${WORKDIR}/ledger-live-desktop

    # Add coin to list of supported currencies
    #sed -i -- "s/setSupportedCurrencies(\[/setSupportedCurrencies(\[\"${COIN}\",/g" \
    #    src/live-common-set-supported-currencies.js

    # yalc add @ledgerhq/live-common
    #yalc add @ledgerhq/ledger-core

    # Ensure versions are matching
    # sed -i -- 's/5.26.0/5.28.0/g' package.json
    #sed -i -- 's/5.19.1/5.22.0/g' package.json

    # yarn install
)


if [ $? -eq 0 ]; then
    alias_cli_command="${LEDGER_LIVE_OPTIONS} node ${WORKDIR}/ledger-live-common/cli/bin/index.js"
    alias_desktop_command="${LEDGER_LIVE_OPTIONS} cd ${WORKDIR}/ledger-live-desktop && yarn start"

    alias ledger-live="${alias_cli_command}"
    alias ledger-desktop="${alias_desktop_command}"

    echo "Please copy/paste the following aliases:"
    echo "alias ledger-live=\"${alias_cli_command}\""
    echo "alias ledger-desktop=\"${alias_desktop_command}\""
fi