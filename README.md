# ApiX CLI



_**ApiX** Command Line Tool_



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

python3 setup.py check

```

Build distribution

```

python3 setup.py sdist

```

or

```

python3 -m build

```

Upload package to Pypi repo

```

twine upload --repository-url https://test.pypi.org/legacy/ dist/*

```

Test package

```

pip install -i https://test.pypi.org/simple/ apixdev==0.2.0

```



Finnaly, upload to Pypi

```

twine upload dist/*

```

## Test package with Docker

```
./test_python310.sh
```
or
```
docker run -v `pwd`:`pwd` -w `pwd` --name pytest -it -d python:3.10
docker exec -it pytest bash
```

```
$ pip install -e .
$ apix [...]
```
```
./clear.sh
```
or
```
docker stop pytest && docker rm pytest
```
