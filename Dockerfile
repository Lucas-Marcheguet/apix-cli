FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir
RUN pip install -i https://test.pypi.org/simple/ -r requirements.txt

CMD [ "bash" ]
