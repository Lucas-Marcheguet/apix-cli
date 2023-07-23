#!/usr/bin/bash

docker run -v `pwd`:`pwd` -w `pwd` --name test_python310 -it -d python:3.10
docker exec -it test_python310 bash
