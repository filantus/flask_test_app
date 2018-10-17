import os
import tempfile
import uuid
import json
import pytest
import logging
from typing import Union
from main import app, db_init


def version_uuid(uuid_string: str):
    try:
        return uuid.UUID(str(uuid_string)).version
    except ValueError:
        pass


def valid_json(string: Union[str, bytes]) -> bool:
    try:
        json.loads(string)
        return True
    except json.decoder.JSONDecodeError:
        return False


car_data = {
    'color': 'yellow',
    'trip': 20000,
    'year': 2010,
    'vendor': 'Hyundai',
    'model': 'Getz',
}

car_data2 = {
    'color': 'null',
    'trip': 0,
    'year': -1,
    'vendor': '',
    'model': None,
}

component_data = {
    'type': 'engine',
    'number': 'VIN1234',
    'car_uid': '',
}


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db_fd, app.config['DATABASE'] = tempfile.mkstemp(prefix='flask_main_test_', suffix='.sqlite')
        logging.disable(logging.INFO)
        db_init(app)
        logging.disable(logging.NOTSET)

    yield client

    os.close(db_fd)
    try:
        os.unlink(app.config['DATABASE'])
    except PermissionError:
        pass


def test_create_car(client):
    """Ответ сервера при создании машины должен быть в json формате"""
    r = client.post('/api/car', json=car_data, follow_redirects=False)
    assert valid_json(r.data)


def test_create_car_without_data(client):
    """Запрос на создание машины без указания данных должен возвращать
       корренктный json.
    """
    r = client.post('/api/car', follow_redirects=False)
    assert valid_json(r.data)


def test_create_car_return_valid_uid(client):
    """Поле uid должно быть правильного формата (UUID)"""
    r = client.post('/api/car', json=car_data, follow_redirects=False)
    data = r.get_json()
    assert version_uuid(data.get('uid')) > 0


def test_create_car_return_valid_data(client):
    """Данные, которые мы передаём для создания машины, должны совпадать
       с данными которые мы получаем в ответе.
       Пустые строки должны быть заменены на None(null)
    """
    for test_car_data in (car_data, car_data2):
        r = client.post('/api/car', json=test_car_data, follow_redirects=False)
        data = r.get_json()
        for key, value in test_car_data.items():
            value = value or None
            assert value == data.get(key)


def test_get_car(client):
    """GET Запрос на получанеи машины по uid должен возвращать данные в json формате.
       uid по которому мы запрашиваем машину должен совпадать с uid в данных по
       машине которые мы получаем в ответ.
    """
    r = client.post('/api/car', json=car_data, follow_redirects=False)
    uid = json.loads(r.data).get('uid')
    r = client.get('/api/car/%s' % uid, follow_redirects=False)
    data = r.get_json()

    assert valid_json(r.data)
    assert uid == data.get('uid')


def create_component(client, raw: bool=False, with_car: bool=False):
    """Создание машины, а затем компонента с привязкой к этой машине.
    :param raw - Если True то возвращает json данные компонента как строку.
                 Если False то возвращает данные компонента как dict.
    :param with_car - Если True то возвращает tuple с данными машины(dict)
                      и данными компонента (dict).
                      Если False то возвращает данные компонента (dict).
    """
    r = client.post('/api/car', json=car_data, follow_redirects=False)
    tmp_car_data = r.get_json()

    tmp_component_data = component_data.copy()
    tmp_component_data['car_uid'] = tmp_car_data.get('uid')

    r = client.post('/api/component', json=tmp_component_data, follow_redirects=False)
    if raw:
        return r.data
    if with_car:
        return tmp_car_data, r.get_json()
    return r.get_json()


def test_create_component(client):
    """Ответ сервера при создании компонента должен быть в json формате"""
    assert valid_json(create_component(client, raw=True))


def test_create_component_no_root_car_uid(client):
    """В корне json данных компонента не должно быть car_uid"""
    assert 'car_uid' not in create_component(client).keys()


def test_create_component_valid_car(client):
    """Доступ к car.uid"""
    tmp_car_data, tmp_component_data = create_component(client, with_car=True)
    assert tmp_car_data.get('uid') == tmp_component_data['car'].get('uid')
