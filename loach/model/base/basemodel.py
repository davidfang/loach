# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base

Modle = declarative_base()


class BaseModel(Modle):
    __abstract__ = True
    __key__ = None
    __db__ = None

    @classmethod
    def get(cls, key):
        with cls.__db__.session_context() as session:
            record = session.query(cls).filter(getattr(cls, cls.__key__) == key).first()
            if record:
                return record

    @classmethod
    def gets(cls, key):
        with cls.__db__.session_context() as session:
            records = session.query(cls).filter_by(getattr(cls, cls.__key__) == key).all()
            if records:
                return records

    @classmethod
    def execute(cls, type, sql, **kwargs):
        with cls.__db__.session_context(autocommit=True) as session:
            data = {}
            result = session.execute(sql.replace(':t_name', cls.__table_args__['schema']+'.'+cls.__tablename__).replace(':key_id', cls.__key__), kwargs)
            data['rowcount'] = result.rowcount
            if type.lower() == 'select':
                data['rows'] = [dict(zip(row._keymap, row._row)) for row in result.fetchall()]
        return data