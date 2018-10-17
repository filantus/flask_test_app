import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.event import listen
from sqlalchemy_mixins.session import SessionMixin
from sqlalchemy_mixins import AllFeaturesMixin
from sqlalchemy_utils import UUIDType
import uuid


Base = declarative_base()


def db_init(app):
    engine = create_engine(f'sqlite:///{app.config["DATABASE"]}', echo=True)
    session = scoped_session(sessionmaker(bind=engine, autocommit=True, autoflush=True))
    Base.metadata.create_all(engine)
    BaseModel.set_session(session)


def listen_for(targets, identifier, *args, **kw):
    def decorate(fn):
        for target in targets:
            listen(target, identifier, fn, *args, **kw)
        return fn
    return decorate


class BaseModel(Base, AllFeaturesMixin, SessionMixin):
    __abstract__ = True

    def data(self) -> dict:
        keys = [col.key for col in self.__table__.columns]
        return {k: self.__getattribute__(k) for k in keys}


class UUIDModel:
    uid = None

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.uid}>'


class Car(UUIDModel, BaseModel, AllFeaturesMixin):
    __tablename__ = 'car'
    uid = sa.Column(UUIDType(binary=False), primary_key=True)
    color = sa.Column(sa.String)
    trip = sa.Column(sa.Float)
    year = sa.Column(sa.SmallInteger)
    model = sa.Column(sa.String)
    vendor = sa.Column(sa.String)


class Component(UUIDModel, BaseModel, AllFeaturesMixin):
    __tablename__ = 'car_component'
    uid = sa.Column(UUIDType(binary=False), primary_key=True)
    type = sa.Column(sa.String)
    number = sa.Column(sa.String)
    car_uid = sa.Column(sa.String, sa.ForeignKey('car.uid'))

    @hybrid_property
    def car(self):
        if self.car_uid:
            return Car.where(uid=self.car_uid).first()

    @car.setter
    def car(self, value):
        if not value:
            self.car_uid = None
            return

        car_object = value if isinstance(value, Car) else Car.where(uid=str(value)).first()

        if car_object:
            self.car_uid = str(car_object.uid)

    def data(self) -> dict:
        data = super().data()
        data['car'] = self.car.data() if self.car else None
        del data['car_uid']
        return data


@listen_for((Car, Component), 'before_insert')
def gen_uuid(mapper, connect, self):
    self.uid = str(uuid.uuid4())
