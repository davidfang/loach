# -*- coding: utf-8 -*-
import datetime
from loach.model.base.basemodel import BaseModel
from loach.model import douyindb
from sqlalchemy import Column, Boolean, Integer, String, DateTime


class DouYinFollowRelation(BaseModel):
    __tablename__ = 'tar_douyin_follow_relation'
    __db__ = douyindb
    __key__ = 'user_id'
    __table_args__ = {
        "schema": "douyindb_test"
    }

    #  元数据
    id = Column(Integer, primary_key=True, autoincrement=True, comment=u'记录 id')
    create_time = Column(DateTime, nullable=False,
                         default=datetime.datetime.now, comment=u'记录创建时间')
    # 基本数据，可通过 PC 端获取
    user_id = Column(String, nullable=False, default='', comment=u'作者 id')
    follower_id = Column(String, nullable=False, default='', comment=u'')

    @classmethod
    def add(cls, user_id=None, **kwargs):
        obj = cls(user_id=user_id, **kwargs)
        with cls.__db__.session_context(autocommit=True) as session:
            session.add(obj)

    @classmethod
    def add_all(cls, objs):
        relations = [cls(**obj) for obj in objs]
        with cls.__db__.session_context(autocommit=True) as session:
            session.add_all(relations)

    @classmethod
    def exists(cls, user_id=None, follower_id=None):
        with cls.__db__.session_context() as session:
            record = session.query(cls).filter(cls.user_id == user_id, cls.follower_id == follower_id).first()
            if record:
                return True
            else:
                return False

    @classmethod
    def upsert(cls, **kwargs):
        with cls.__db__.session_context(autocommit=True) as session:
            records = session.query(cls).with_for_update().filter(cls.user_id == kwargs['user_id'], cls.follower_id == kwargs['follower_id'])
            if records.first():
                rows_count = records.update({k: v for k, v in kwargs.items()})
                return rows_count
            else:
                session.add(cls(**kwargs))
