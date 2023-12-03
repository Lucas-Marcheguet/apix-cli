
# apix

_**ApiX** Command Line Tool_

![PyPI](https://img.shields.io/pypi/v/apix-cli)
![PyPI](https://img.shields.io/pypi/pyversions/apix-cli)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/apikcloud/apix-cli)


## Installation

Install from PyPI:

```bash
pip install apix-cli
```

## Quickstart

*On first launch, you will be asked to enter certain parameters.*

Create project :

`project name` is the name of the online database you want to create locally.
```bash
apix project new <project name>
```

Run project :

```bash
apix project run <project name> --reload
```

Update modules :

```bash
apix project update-modules <project name> <database name> module1,module2
```

## Documentation

Please refer to :
[https://apikcloud.github.io/apix-cli/](https://apikcloud.github.io/apix-cli/)
