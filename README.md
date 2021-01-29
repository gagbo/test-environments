# test-environments

Scripts to setup reproductible test environments for `live-common` and `Vault`.

## Prerequisites

* OS: Linux or macOS
* Nvm (https://github.com/nvm-sh/nvm)
* Python 3 (https://www.python.org/downloads/)
* `PyYAML` Python package (https://pypi.org/project/PyYAML/)
* Yarn
* Node 12 (Linux: `nvm install 12`; macOS: `nvm install 12 64`)
* yalc (https://www.npmjs.com/package/yalc)

**Windows**

- Install Git bash
- Using CMD/PowerShell as Admin: install `windows-build-tools`: `npm install --global windows-build-tools`
- Using CMD/PowerShell as Admin: install `node-gyp`: `npm install --global node-gyp`
- Using Git Bash as Admin, run `winpty "<path>\python.exe" -m pip install termcolor` (example: `winpty "C:\Program Files\Python39\python.exe" -m pip install termcolor`)

### Run

#### Option 0: Do not compile libcore (Coin implemented using JS)

**MacOS/Linux**
```
$ ./setup_live.py <coin name>
```

Example:
```
$ ./setup_live.py polkadot
```

**Windows (from Git Bash as Admin)**
```
$ winpty "C:\Program Files\Python39\python.exe" setup_live.py <coin name>
```

Example:
```
$ winpty "C:\Program Files\Python39\python.exe" setup_live.py polkadot
```


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
            <optional: commit: <SHA1>>
        live_common:
            repository: <repository uri> 
            branch: <branch name>
        options:
            - <optional: option #1>
            - <optional: option #2>
            - <optional: option #3 . . .>
```

If a `commit` key-value pair is added, the checkout is done using the corresponding SHA1. Otherwise, the checkout is done using the branch name. 

For instance,

```
repository: git@github.com:Ledger-Coin-Integration-team/lib-ledger-core-node-bindings.git
branch: int-algorand
```

corresponds to a `git checkout int-algorand-libcorev1`.

By contrast,

```
repository: git@github.com:Ledger-Coin-Integration-team/lib-ledger-core-node-bindings.git
branch: int-algorand
commit: 268ac614a77498dd312fb7d576cbd98324cfb49e
```

corresponds to a `git checkout 268ac614a77498dd312fb7d576cbd98324cfb49e && git reset --hard`.