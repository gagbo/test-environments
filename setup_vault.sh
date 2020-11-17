#!/bin/bash
set -e

COIN=${1}
PRODUCT='vault'
SCRIPT_DIR="$(pwd)"
WORKDIR="${SCRIPT_DIR}/.${PRODUCT}_sources"

source common.sh

export VAULT_PROFILE=front
#export WALLET_DAEMON_VERSION=custom

remove_image() {
    docker rmi $( docker images ls | grep ${1} ) --force || true
}

check_image() {
    if [[ $( docker image ls | grep ${1} ) != *"${1}"* ]]; then
        echo "${1} image not found" && return 1
    fi
}

check_container() {
    if [[ $( docker ps | grep ${1} ) != *"${1}"* ]]; then
        echo "${1} container not found" && return 1
    fi
}

# Prerequisite: node v10
set_node 10

# Stop containers that are currently running
docker stop $(docker ps -a -q) || true


# LIBCORE
#retrieve_sources 'libcore'

# Temporary: to remove when the corresponding Dockerfile is merged into libcore
#   context: https://github.com/Ledger-Coin-Integration-team/lib-ledger-core/pull/60
#mkdir -p tools/builder
#cp -v ../../Dockerfile tools/builder/Dockerfile

# Compile and encapsulate in JAR file
#remove_image "libcore"
#docker build -t libcore --build-arg BUILD_TYPE=Release -f tools/builder/Dockerfile .
#check_image "libcore"


# WALLET DAEMON
#retrieve_sources 'wallet_daemon'

# Put newly generated .jar in lib subdirectory
#cd lib
#rm *
#docker run -v $(pwd):/build libcore
#stat ledger-lib-core.jar # (assert that JAR file has been retrieved)

#cd ..

# Build custom wallet-daemon image
#remove_image "ledger-wallet-daemon"
#docker build -t ledgerhq/ledger-wallet-daemon:${WALLET_DAEMON_VERSION} .
#check_image "ledger-wallet-daemon"


# VAULT INTEGRATION
retrieve_sources 'vault_integration'

python3 -m venv .venv

source .venv/bin/activate

pip3 install -r requirements.txt

inv flush setup.qa up -d


# VAULT FRONT
retrieve_sources 'vault_front'

yarn cache clean
git clean -xdf
rm -rf node_modules/

yarn

yarn dev &