# test-environments

Scripts to setup reproductible test environments for `live-common`.

## Prerequisites

* Python 3 (https://www.python.org/downloads/)
* Nvm (https://github.com/nvm-sh/nvm)
* Yarn (https://classic.yarnpkg.com/en/docs/install/)
* Node 12 (Linux: `nvm install 12`; macOS: `nvm install 12 64`)
* yalc (https://www.npmjs.com/package/yalc)
* yarn-deduplicate: `npm i -g yarn-deduplicate`

**Windows**

- Install Git bash
- Using CMD/PowerShell as Admin: install `windows-build-tools`: `npm install --global windows-build-tools`
- Using CMD/PowerShell as Admin: install `node-gyp`: `npm install --global node-gyp`
- Using Git Bash as Admin, run `winpty "<path>\python.exe" -m pip install -r requirements.txt` (example: `winpty "C:\Program Files\Python39\python.exe" -m pip install -r requirements.txt`)

**Mobile testing**

// TODO

### Run

**MacOS/Linux**
```
$ ./setup_live.py -c <coin name>
```

Example:
```
$ ./setup_live.py -c polkadot
```

**Windows (from Git Bash as Admin)**
```
$ winpty "C:\Program Files\Python39\python.exe" setup_live.py -c <coin name>
```

Example:
```
$ winpty "C:\Program Files\Python39\python.exe" setup_live.py -c polkadot
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
