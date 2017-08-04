import sqlite3
import sys
import os
import pickle
from sqlalchemy import Column, Integer, String, UniqueConstraint, create_engine, exc, orm, MetaData, inspect
from sqlalchemy.schema import Sequence
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager


DBNAME = 'name_server'
folder = os.path.dirname(os.path.realpath(__file__))
DSN = 'sqlite:///{path}.db'.format(path=os.path.join(folder, DBNAME))


Base = declarative_base()

class Service(Base):
    __tablename__ = 'services'
    id = Column('id', Integer, primary_key=True)
    host = Column('host', String)
    port = Column('port', Integer)
    name = Column('name', String)
    description = Column('description', String)
    __table_args__ = (UniqueConstraint('host', 'port', name='address_cnt'),)

    def __repr__(self):
        return "<Service(name='{name}', address='{addr}', description='{desc}')>".format(name=self.name,
                                                                                         addr=self.address,
                                                                                         desc=self.description)
    def __str__(self):
        return repr(self)


    @property
    def address(self):
        return '{host}:{port}'.format(host=self.host, port=self.port)


class DatabaseAdapter(object):

    def __init__(self, dsn):
        try:
            eng = create_engine(dsn)
        except Exception as err:
            raise
        self.Session = orm.sessionmaker(bind=eng)
        self.services = Service.__table__
        self.eng = self.metadata.bind = eng
        self.metadata.create_all(checkfirst=True)


    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as error:
            session.rollback()
            raise
        finally:
            session.close()


    def upsert(self, obj):
        with self.session_scope() as ses:
            query = ses.query(Service).filter(Service.host==obj.host, Service.port==obj.port)
            if query.count():
                query.update({Service.name: obj.name,
                              Service.description: obj.description or Service.description
                             })
            else:
                ses.add(obj)


    def get_service_by_name(self, name):
        with self.session_scope() as ses:
            query = ses.query(Service).filter(Service.name==name)
            total = query.count()
            if total > 1:
                msg = 'There are several services with the name `{name}`:\n'.format(name=name)
                for i,service in enumerate(query):
                    msg += '{idx}. {service}\n'.format(idx=i+1, service=service)
            elif total == 1:
                msg = 'Address of the requested service is {addr}'.format(addr=query.one().address)
            else:
                msg = 'Sorry, there is no service with the name `{name}`'.format(name=name)
            return msg


    def __getattr__(self, attr):
        return getattr(self.services, attr)


if __name__=='__main__':
    db = DatabaseAdapter(DSN)

