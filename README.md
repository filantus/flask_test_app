## flask_test_app
Test Application based on Flask and SQLAlchemy

## Запуск в Docker
```
docker run --name flask_app_test --rm -v $PWD:/app -p 80:80 -it python:3.7-slim-stretch bash
cd /app
pip install -r requirments.txt
```

### Тесты
`pytest -W error::UserWarning`

### Запуск сервера
`python main.py`

## Запуск на Ubuntu 16.04 с Python 3.7

`sudo apt-get update && sudo apt-get upgrade`

```
sudo apt-get install -y build-essential python-dev python-setuptools python-pip libpcre3 libpcre3-dev \
    zlib1g-dev libssl-dev libcurl4-openssl-dev libreadline-dev libyaml-dev libxml2-dev libxslt-dev \
    libgdbm-dev libc6-dev libffi-dev libsqlite3-dev
```

### Установка Python3.7 !!! Важно - перезапишет ваш python3 и все python3 пакеты если таковые имеются !!!
```
cd /tmp && wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz && \
    sudo tar -xvf Python-3.7.0.tgz && cd /tmp/Python-3.7.0/ && \
    sudo ./configure && sudo make && sudo make install && sudo rm -rf /tmp/*
```

```
sudo pip3 install virtualenv
sudo python3 -m virtualenv ./.venv
sudo ./.venv/bin/python ./.venv/bin/pip install -r requirments.txt
```

### Тесты
`./.venv/bin/python ./.venv/bin/pytest -W error::UserWarning`

### Запуск сервера
`./.venv/bin/python main.py`
