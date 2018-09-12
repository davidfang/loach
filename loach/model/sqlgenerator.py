# -*- coding: utf-8 -*-

from loach.model.base.basemodel import Modle
from loach.model import douyindb
from sqlalchemy.schema import CreateSchema
# from loach.model.douyinlikerelation import DouYinLikeRelation
# from loach.model.douyinfollowrelation import DouYinFollowRelation
# from loach.model.douyinaccount import DouYinAccount
# from loach.model.douyinvideo import DouYinVideo
# from loach.model.douyincomment_mul import DouComment
from loach.model.douyinmusic import DouYinMusic
# from loach.model.douyinchallenge import DouYinChallenge
# from loach.model.douyinvideo_mul import DouYinVideo
# douyindb_4.engine.execute(CreateSchema('douyindb_test'))
Modle.metadata.create_all(douyindb.engine)
