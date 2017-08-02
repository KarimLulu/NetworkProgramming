import sqlite3
import sys
import pickle
from sqlalchemy import Column, Integer, String, create_engine, exc, orm


DBNAME = 'name_server'


class DatabaseAdapter(object):

    def __init__(self, dsn):
        try:
            self.engine = create_engine(dsn)
        except Exception as err:
            raise

        try:
            self.engine.connect()
        except:
            raise




