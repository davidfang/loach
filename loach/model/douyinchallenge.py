# -*- coding: utf-8 -*-
import datetime
from loach.model.base.basemodel import BaseModel
from loach.model import douyindb
from sqlalchemy import Column, Boolean, Integer,BigInteger, String, DateTime, Date, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql.dml import Insert

class DouYinChallenge(BaseModel):
    __tablename__ = 'tar_douyin_challenge_info'
    __db__ = douyindb
    __key__ = 'cha_id'
    __table_args__ = {
        "schema": "douyindb_test"
    }

    #  元数据
    id = Column(Integer, primary_key=True, autoincrement=True, comment=u'记录 id')
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now, comment=u'记录创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment=u'记录更新时间')

    # 基本数据，可通过 PC 端获取
    cha_id = Column(String, nullable=False, unique=True, comment=u'id')
    cha_name = Column(String, nullable=False, default='', comment=u'话题')
    description = Column(String, nullable=False, default='', comment=u'话题描述')
    user_count = Column(BigInteger, nullable=False, default=0, comment=u'参与人数')
    view_count = Column(BigInteger, nullable=False, default=0, comment=u'浏览量')
    aweme_list = Column(JSONB, nullable=False, default=list, comment=u'参与作品')

    @classmethod
    def add_with_conflict(cls, **kwargs):
        with cls.__db__.session_context(autocommit=True) as session:
            session.execute(Insert(cls).values(**kwargs).on_conflict_do_update(
                index_elements=[cls.__key__],
                set_=kwargs
            ))

    @classmethod
    def add_all_with_conflict(cls, objs):
        with cls.__db__.session_context(autocommit=True) as session:
            for obj in objs:
                session.execute(Insert(cls).values(**obj).on_conflict_do_update(
                    index_elements=[cls.__key__],
                    set_=obj
                ))
