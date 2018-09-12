# -*- coding: utf-8 -*-
import arrow
from celery import Celery
from celery import chord
from loach.setting import config
from loach.utils import dict_trip
from loach.model.douyinaccount import DouYinAccount
from loach.model.douyinvideo import DouYinVideo
from loach.model.douyincomment import DouComment
from loach.model.douyinlikerelation import DouYinLikeRelation
from loach.model.douyinfollowrelation import DouYinFollowRelation
from loach.model.douyinaccount_mul import DouYinAccount as DYA_MUL
from loach.model.douyinvideo_mul import DouYinVideo as DYV_MUL
from loach.model.douyincomment_mul import DouComment as DYC_MUL
from loach.utils.redisobj import douyin_rds

celery = Celery()
celery.config_from_object(config['CELERY'])

tables_from = [DYA_MUL, DYV_MUL, DYC_MUL]
tables_to = [DouYinAccount, DouYinVideo, DouComment]
# tables_from = [DYA_MUL, ]
# tables_to = [DouYinAccount, ]
models = {
        "tar_douyin_account_info_mul": DYA_MUL,
        "tar_douyin_video_info_mul": DYV_MUL,
        "tar_douyin_comment_info_mul": DYC_MUL,
        "tar_douyin_account_info": DouYinAccount,
        "tar_douyin_video_info": DouYinVideo,
        "tar_douyin_comment_info": DouComment,
    }

@celery.task(
    name='douyin.schedule.database.clean',
    acks_late=True
)
def douyin_schedule_database_clean():
    """
    周期性清洗数据库
    :return:
    """
    # print('timer start')

    date = arrow.now().format('YYYY-MM-DD')
    delete_task = celery.signature('douyin.schedule.database.delete', kwargs={'date': date}, immutable=True)
    chord_copy_tasks = [celery.signature('douyin.schedule.database.copy', args=(table_from.__tablename__, table_to.__tablename__, date), immutable=True) for table_from, table_to in zip(tables_from, tables_to)]

    chord(chord_copy_tasks)(delete_task)


@celery.task(
    name='douyin.schedule.database.copy',
    acks_late=True
)
def douyin_schedule_database_copy(table_from, table_to, date):
    sql_count = 'SELECT count(1) from :t_name as a WHERE create_time<:create_time AND NOT EXISTS (SELECT 1 FROM :t_name as b WHERE create_time<:create_time AND a.:key_id=b.:key_id AND a.id<b.id)'
    sql_rows = 'SELECT * from :t_name as a WHERE create_time<:create_time AND NOT EXISTS (SELECT 1 FROM :t_name as b WHERE create_time<:create_time AND a.:key_id=b.:key_id AND a.id<b.id) ORDER  BY id ASC LIMIT :offset OFFSET :start'

    r = models[table_from].execute('SELECT', sql_count, create_time=date)
    offset = 50000

    if r['rows'][0]['count']:
        # sql = 'SELECT * from :t_name as a WHERE create_time<:create_time AND NOT EXISTS (SELECT 1 FROM :t_name as b WHERE a.:key_id=b.:key_id AND a.id<b.id) ORDER  BY id ASC LIMIT :offset OFFSET :start'
        end = r['rows'][0]['count']
        for start in range(0, end, offset):
            r = models[table_from].execute('select', sql_rows, offset=offset, start=start, create_time=date)
            for row in r['rows']:
                row.pop('id')
                dict_trip(row)
            models[table_to].add_all_with_conflict(r['rows'])
            print(table_from, start)


@celery.task(
    name='douyin.schedule.database.delete',
    acks_late=True
)
def douyin_schedule_database_delete(date):
    print('delete')
    sql = 'delete from :t_name WHERE create_time<:create_time'
    # 千万 千万 千万注意了  tables_from   不是to   删错就得跑路了
    for table in tables_from:
        table.execute('delete', sql, create_time=date)


@celery.task(
    name='douyin.schedule.database.relation.distinct',
    acks_late=True
)
def douyin_schedule_database_relation_distinct(date):
    date = arrow.now().format('YYYY-MM-DD')
    start_date = arrow.get(date).shift(days=-7).format('YYYY-MM-DD')
    sql1 = 'DELETE FROM :t_name AS a \
                        WHERE create_time>=:start_date AND create_time<:date and exists( \
                            SELECT 1 \
                            FROM :t_name AS b \
                            WHERE a.user_id = b.user_id AND a.follower_id = b.follower_id AND a.id < b.id \
                        )'
    sql2 = 'DELETE FROM :t_name AS a \
                        WHERE create_time>=:start_date AND create_time<:date and exists( \
                            SELECT 1 \
                            FROM :t_name AS b \
                            WHERE a.user_id = b.user_id AND a.video_id = b.video_id AND a.id < b.id \
                        )'
    r = DouYinFollowRelation.execute('delete', sql1, start_date=start_date, date=date)
    print('成功删除follow_relation的数据 %d 条' % r['rowcount'])
    DouYinLikeRelation.execute('delete', sql2, start_date=start_date, date=date)


if __name__ == '__main__':
    douyin_schedule_database_copy(table_from='tar_douyin_account_info_mul',table_to='tar_douyin_account_info',date = arrow.now().format('YYYY-MM-DD'))