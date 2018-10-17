import os
import tempfile
import uuid
import pytest
import logging
from main import app, db_init
from models import Car, Component


def version_uuid(uuid_string: str):
    try:
        return uuid.UUID(str(uuid_string)).version
    except ValueError:
        pass


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


@pytest.fixture(scope="function", autouse=True)
def application():
    app.config['TESTING'] = True

    with app.app_context():
        db_fd, app.config['DATABASE'] = tempfile.mkstemp(prefix='flask_main_test_', suffix='.sqlite')
        logging.disable(logging.INFO)
        db_init(app)
        logging.disable(logging.NOTSET)

    yield app

    os.close(db_fd)
    try:
        os.unlink(app.config['DATABASE'])
    except PermissionError:
        pass


def test_create_car():
    """Создание объекта машины и сохранение его в базе данных"""
    car = Car(**car_data)
    car.save()
    assert version_uuid(car.uid)


def test_create_component():
    """Создание объекта компонента и сохранение его в базе данных"""
    component = Component(**component_data)
    component.save()
    assert version_uuid(component.uid)


def create_component_with_car(with_car2=False) -> tuple:
    car = Car(**car_data)
    car.save()

    tmp_component_data = component_data.copy()
    tmp_component_data['car_uid'] = str(car.uid)

    component = Component(**tmp_component_data)
    component.save()

    if with_car2:
        car2 = Car(**car_data)
        car2.save()
        return car, car2, component
    return car, component


def test_create_component_with_car():
    """Создание машины, а затем компонента с привязкой к этой машине."""
    car, component = create_component_with_car()
    assert version_uuid(component.uid)


def test_component_get_car():
    """Свойство компонента "car" должно возвращать либо None либо объект
       типа <class 'main.models.Car'>
    """
    car, component = create_component_with_car()
    assert isinstance(component.car, Car)


def test_component_set_car_by_car_obj():
    """У компонента есть свойство "car", оно должно иметь возможность принимать
      значения. Принимаемые типы значений: <class 'main.models.Car'>,
      <class 'uuid.UUID'>, <class 'str'>, <class 'NoneType'>.
    """
    car, car2, component = create_component_with_car(with_car2=True)

    component.car = car2
    assert component.car.uid == car2.uid
    assert isinstance(component.car, Car)


def test_component_set_car_by_uuid_obj():
    car, car2, component = create_component_with_car(with_car2=True)

    component.car = car2.uid
    assert component.car.uid == car2.uid
    assert isinstance(component.car, Car)


def test_component_set_car_by_uuid_str():
    car, car2, component = create_component_with_car(with_car2=True)

    component.car = str(car2.uid)
    assert component.car.uid == car2.uid
    assert isinstance(component.car, Car)


def test_component_unset_car():
    car, component = create_component_with_car()
    component.car = None
    assert component.car is None
