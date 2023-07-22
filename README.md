# Apixdev

_Apix Developper Toolkit_

----------
## Quickstart
```
pip install apixdev
```
```
apix
```
## Developpment
```
pip install -e .
```
## Build
```
pip install twine
```
Check setup.py
```
python setup.py check
```
Build distribution
```
python setup.py sdist
```
or
```
python3 -m build
```
Upload package to Pypi repo
```
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
```
twine upload dist/*
```
