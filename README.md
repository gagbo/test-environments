# test-environments

## Prerequisites (common to all scripts)

* Nvm
* Python 3

## Live-common

The `setup_live.sh` script:
* Compiles `lib-ledger-core` (build type: Release, target: host OS)
* Creates the bindings
* Associates them with `live-common` using yalc

### Prerequisites

* Node 12 (Linux: `nvm install 12`; macOS: `nvm install 12 64`)
* `PyYAML` Python package (https://pypi.org/project/PyYAML/)
* yalc

### Run

```
. ./setup.sh <coin name>
ledger-live . . .
```

Example:

```
. ./setup.sh algorand
ledger-live sync -c algorand
```

## Vault

The `setup_vault.sh` script:
* Compiles `lib-ledger-core` (build type: Release, target: Linux (Debian))
* Encapsulates the resulting compiled library in a JAR file
* Builds a custom `ledger-wallet-daemon` Docker image embedding this JAR file
* Runs the components of the Vault

### Prerequisites

* Docker
* Docker Compose
* Node 10 (Linux: `nvm install 10`; macOS: `nvm install 10 64`)
* Default Vault environment variables (set and sourced, or set in `.env` file)
* `click` Python package (https://pypi.org/project/click/) (for `vault-integration`, `./vault_compose` command)
* Logged in to Docker Hub from account belonging to `ledgerhq` organization

### Setup

In `setup_vault.sh`, check the Vault-related environment variables (if needed, add those that have to overload the default ones).

### Run

`./setup_vault.sh <coin name>`

Example:

`./setup_vault.sh algorand`

## Configure a new coin

Edit `config.yml` by adding the configuration details related to the new coin with the following structure:

```
<coin_name>:
    live:
        libcore:
            repository: <repository uri> 
            branch: <branch name>
        bindings:
            repository: <repository uri> 
            branch: <branch name>
        live_common:
            repository: <repository uri> 
            branch: <branch name>
        cli_options:
            - <optional: CLI option #1>
            - <optional: CLI option #2>
            - <optional: CLI option #3 . . .>
    vault:
        libcore:
            repository: <repository uri> 
            branch: <branch name>
        wallet_daemon:
            repository: <repository uri> 
            branch: <branch name>
        vault_integration: 
            repository: <repository uri> 
            branch: <branch name>
        vault_front:
           repository: <repository uri> 
            branch: <branch name>
```
