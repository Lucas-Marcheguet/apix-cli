# ApiX CLI

This page provides documentation for our command line tools.

----------

## Installation

Install from PyPI:
```bash
pip install apixdev
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
