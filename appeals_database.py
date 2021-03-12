import os

from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relation
from werkzeug.security import check_password_hash

engine = create_engine(f"sqlite:///{os.path.join('db', 'db.sqlite')}",
                       connect_args={"check_same_thread": False})
Base = declarative_base()


class Engineer(Base, UserMixin):
    __tablename__ = "engineer"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(Integer, nullable=False)
    appeals = relation("Appeal", back_populates="worker")

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Appeal(Base):
    __tablename__ = "appeal"

    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    kind = Column(String, nullable=False)
    worker_id = Column(Integer, ForeignKey("engineer.id"))
    worker = relation("Engineer", back_populates="appeals", lazy='joined')


class AppealsDatabase:

    def __init__(self):
        Base.metadata.create_all(engine)

    @staticmethod
    def get_session():
        return scoped_session(sessionmaker(bind=engine))

    def add(self, appeal: Appeal):
        session = self.get_session()
        session.add(appeal)
        session.commit()

    def get_all(self):
        return self.get_session().query(Appeal).all()

    def take(self, appeal_id, engineer_id):
        session = self.get_session()
        engineer = session.query(Engineer)\
            .filter(Engineer.id == engineer_id)\
            .first()
        session.query(Appeal)\
            .filter(Appeal.id == appeal_id)\
            .first().worker = engineer
        session.commit()


class EngineersDatabase:

    def __init__(self):
        Base.metadata.create_all(engine)

    @staticmethod
    def get_session():
        return scoped_session(sessionmaker(bind=engine))

    def add(self, engineer: Engineer):
        session = self.get_session()
        session.add(engineer)
        session.commit()

    def by_email(self, email):
        return self.get_session()\
            .query(Engineer)\
            .filter(Engineer.email == email)\
            .first()

    def by_id(self, engineer_id):
        return self.get_session()\
            .query(Engineer)\
            .filter(Engineer.id == engineer_id)\
            .first()
