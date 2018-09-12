# -*- coding: utf-8 -*-
"""
原来的数据清洗程序速度极慢，无法满足每日100w的增量， 原因： 频繁的update，select请求数据库

改进方案： 1。 为每个表创建辅助表，所有爬虫抓到的数据清洗过后直接全部存在对应的辅助表，
          2。后期一并去重入库
"""
import os
import sys
import traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/../../")
import pika
import json
import datetime
from loach.model.douyinaccount_mul import DouYinAccount as DYA_MUL
from loach.model.douyinfollowrelation import DouYinFollowRelation
from loach.model.douyinlikerelation import DouYinLikeRelation
from loach.model.douyinmusic import DouYinMusic
from loach.model.douyinvideo_mul import DouYinVideo as DYV_MUL
from loach.model.douyincomment_mul import DouComment as DYC_MUL
from loach.model.douyinchallenge import DouYinChallenge
from json.decoder import JSONDecodeError

con = pika.BlockingConnection(pika.ConnectionParameters(host='xxx', port=5672, virtual_host='/', credentials=pika.PlainCredentials('xxx', 'xxx')))
channel = con.channel()



binding_keys = [
    # routing_key       queue_name
    'douyin.author.#', 'douyin.author'
]


def douyin_author_post(data):
    videos = data['aweme_list']
    videos_cleared = list()
    for video in videos:
        video_cleared = {
            'user_id': str(video['author_user_id']),
            'short_id': video['author']['short_id'],
            'video_id': video['aweme_id'],
            'cover': video['video']['cover']['url_list'][0],
            'description': video['desc'],
            'comment_count': video['statistics']['comment_count'],
            'share_count': video['statistics']['share_count'],
            'like_count': video['statistics']['digg_count'],
            'play_count': video['statistics']['play_count'],
            'share_url': video['share_info']['share_url'],
            # 'age':
            'status': 0,
            'video_create_time': datetime.datetime.fromtimestamp(video['create_time'])
        }
        for play_url in video['video']['play_addr']['url_list']:
            if play_url.find('aweme.snssdk') > 0:
                video_cleared['play_url'] = play_url
                break
        videos_cleared.append(video_cleared)
    DYV_MUL.add_all(videos_cleared)
    return 'OK'


def douyin_author_feed(data):
    videos = data['aweme_list']
    videos_cleared = list()
    for video in videos:
        video_cleared = {
            'user_id': str(video['author_user_id']),
            'short_id': video['author']['short_id'],
            'video_id': video['aweme_id'],
            'cover': video['video']['cover']['url_list'][0],
            'description': video['desc'],
            'comment_count': video['statistics']['comment_count'],
            'share_count': video['statistics']['share_count'],
            'like_count': video['statistics']['digg_count'],
            'play_count': video['statistics']['play_count'],
            'share_url': video['share_info']['share_url'],
            # 'age':
            'status': 0,
            'video_create_time': datetime.datetime.fromtimestamp(video['create_time'])
        }
        for play_url in video['video']['play_addr']['url_list']:
            if play_url.find('aweme.snssdk') > 0:
                video_cleared['play_url'] = play_url
                break
        videos_cleared.append(video_cleared)
    DYV_MUL.add_all(videos_cleared)
    return 'OK'


def douyin_author_following(response):
    authors_info = response['followings']
    uid = response['uid']
    authors_cleared = list()
    relations = list()
    for author_info in authors_info:
        author_info_cleared = {
            'user_id': str(author_info.get('uid')),
            'description': author_info.get('signature'),
            'nickname': author_info.get('nickname'),
            'short_id': author_info.get('short_id'),
            'avatar': author_info['avatar_thumb']['url_list'][0],
            'verification_type': author_info.get('verification_type'),
            'birthday': author_info.get('birthday'),
            # 'age':
            'sex': author_info.get('gender'),
            'region': author_info.get('region'),
            'account_create_time': datetime.datetime.fromtimestamp(author_info.get('create_time', 0))
        }
        if 2 == author_info_cleared['verification_type']:
            author_info_cleared['verification'] = '抖音音乐人'
        relation = {
            "user_id": author_info_cleared['user_id'],
            "follower_id": uid
        }
        authors_cleared.append(author_info_cleared)
        relations.append(relation)
    DYA_MUL.add_all(authors_cleared)
    DouYinFollowRelation.add_all(relations)

    return "OK"


def douyin_author_info(author_info):
    author_info_cleared = {
        'user_id': str(author_info.get('uid')),
        'description': author_info.get('signature'),
        'nickname': author_info.get('nickname'),
        'short_id': author_info.get('short_id'),
        'douyin_id': author_info.get('unique_id'),
        'avatar': author_info['avatar_thumb']['url_list'][0],
        'verification': author_info.get('custom_verify'),
        'birthday': author_info.get('birthday'),
        # 'age':
        'sex': author_info.get('gender'),
        'region': author_info.get('location'),
        'like_count': author_info.get('favoriting_count'),
        'video_count': author_info.get('aweme_count'),
        'liked_count': author_info.get('total_favorited'),
        'music_count': author_info['original_musician']['music_count'],
        'music_like_count': author_info['original_musician']['digg_count'],
        'music_used_count': author_info['original_musician']['music_used_count'],
        'following_num': author_info.get('following_count'),
        'follower_num': author_info.get('follower_count'),
    }
    if author_info_cleared['verification'].find("音乐人") >= 0:
        author_info_cleared['verification_type'] = 2
    DYA_MUL.add(**author_info_cleared)
    return "OK"


def douyin_author_favorite(data):
    videos = data['aweme_list']
    uid = data['uid']
    videos_cleared = list()
    relations = list()
    for video in videos:
        video_cleared = {
            'user_id': str(video['author_user_id']),
            'short_id': video['author']['short_id'],
            'video_id': video['aweme_id'],
            'cover': video['video']['cover']['url_list'][0],
            'description': video['desc'],
            'comment_count': video['statistics']['comment_count'],
            'share_count': video['statistics']['share_count'],
            'like_count': video['statistics']['digg_count'],
            'play_count': video['statistics']['play_count'],
            'share_url': video['share_info']['share_url'],
            # 'age':
            'status': 0,
            'video_create_time': datetime.datetime.fromtimestamp(video['create_time'])
        }
        for play_url in video['video']['play_addr']['url_list']:
            if play_url.find('aweme.snssdk') > 0:
                video_cleared['play_url'] = play_url
                break
        relation = {
            "user_id": uid,
            "video_id": video_cleared['video_id']
        }
        videos_cleared.append(video_cleared)
        relations.append(relation)
    DYV_MUL.add_all(videos_cleared)
    DouYinLikeRelation.add_all(relations)

    return 'OK'


def douyin_author_follower(response):
    authors_info = response['followers']
    uid = response['uid']
    authors_cleared = list()
    relations = list()
    for author_info in authors_info:
        author_info_cleared = {
            'user_id': str(author_info.get('uid')),
            'description': author_info.get('signature'),
            'nickname': author_info.get('nickname'),
            'short_id': author_info.get('short_id'),
            'avatar': author_info['avatar_thumb']['url_list'][0],
            'verification_type': author_info.get('verification_type'),
            'birthday': author_info.get('birthday'),
            # 'age':
            'sex': author_info.get('gender'),
            'region': author_info.get('region'),
            'account_create_time': datetime.datetime.fromtimestamp(author_info.get('create_time', 0))
        }
        if 2 == author_info_cleared['verification_type']:
            author_info_cleared['verification'] = '抖音音乐人'
        relation = {
            "user_id": uid,
            "follower_id": author_info_cleared['user_id']
        }
        authors_cleared.append(author_info_cleared)
        relations.append(relation)
    DYA_MUL.add_all(authors_cleared)
    DouYinFollowRelation.add_all(relations)

    return "OK"


def douyin_author_comment(response):
    comments_info = response['comments']
    comments_cleared = list()
    authors_cleared = list()
    for comment_info in comments_info:
        user = comment_info['user']
        comment_info_cleared = {
            'user_id': str(user['uid']),
            'text': comment_info['text'],
            'nickname': user['nickname'],
            'short_id': user['short_id'],
            'video_id': comment_info['aweme_id'],
            'reply_id': comment_info['reply_id'],
            'comment_id': comment_info['cid'],
            'like_count': comment_info['digg_count'],
            'status': comment_info['status'],
            'comment_create_time': datetime.datetime.fromtimestamp(comment_info['create_time'])
        }
        author_info_cleared = {
            'user_id': str(user['uid']),
            'description': user['signature'],
            'nickname': user['nickname'],
            'short_id': user['short_id'],
            'avatar': user['avatar_thumb']['url_list'][0],
            'verification': user['custom_verify'],
            'birthday': user['birthday'],
            'sex': user['gender'],
            'region': user['region'],
            'account_create_time': datetime.datetime.fromtimestamp(user['unique_id_modify_time'])
        }
        authors_cleared.append(author_info_cleared)
        comments_cleared.append(comment_info_cleared)
    DYA_MUL.add_all(authors_cleared)
    DYC_MUL.add_all(comments_cleared)

    return "OK"


def douyin_music_detail(response):
    music_info = response['music_info']
    music_cleared = {
        'music_id': str(music_info['mid']),
        'music_title': music_info['title'],
        'author_id': music_info['owner_id'],
        'author_name': music_info['owner_nickname'],
        'duration': music_info['duration'],
        'user_count': music_info['user_count'],
        'play_url': music_info['play_url']['uri'],
    }
    user = {
        'user_id': str(music_info['owner_id']),
        'nickname': music_info['owner_nickname'],
        'short_id': music_info['owner_id'],
        'douyin_id': music_info['owner_handle'],
        'avatar': music_info['cover_thumb']['url_list'][0]
    }
    DouYinMusic.add_with_conflict(**music_cleared)
    DYA_MUL.add(**user)
    return 'OK'


def douyin_category(response):
    category_list = response['category_list']
    for category in category_list:
        try:
            if category['desc'] == '热门音乐':
                douyin_music_recomend(category['music_info'], category['aweme_list'])
            elif category['desc'] == '热门话题':
                douyin_challenge_recomend(category['challenge_info'], category['aweme_list'])
        except KeyError:
            pass

    return 'OK'


def douyin_challenge_recomend(cha, aweme_list):
    challenge = {
        'cha_id': str(cha['cid']),
        'cha_name': cha['cha_name'],
        'description': cha['desc'],
        'user_count': cha['user_count'],
        'view_count': cha['view_count']
    }
    videos = []
    aweme_ids = []
    for aweme in aweme_list:
        video = {
            'user_id': str(aweme['author_user_id']),
            'video_id': str(aweme['aweme_id']),
            'cover': aweme['video']['cover']['url_list'][0],
            'description': aweme['desc'],
            'comment_count': aweme['statistics']['comment_count'],
            'share_count': aweme['statistics']['share_count'],
            'like_count': aweme['statistics']['digg_count'],
            'video_create_time': datetime.datetime.fromtimestamp(aweme['create_time']),
            'share_url': aweme['share_info']['share_url']
        }
        for play_url in aweme['video']['play_addr']['url_list']:
            if play_url.find('aweme.snssdk') > 0:
                video['play_url'] = play_url
                break
        videos.append(video)
        aweme_ids.append(video['video_id'])
    challenge['aweme_list'] = aweme_ids

    DYV_MUL.add_all(videos)
    DouYinChallenge.add_with_conflict(**challenge)


def douyin_music_recomend(music_list, aweme_list):
    music_cleared = {
        'music_id': str(music_list['mid']),
        'music_title': music_list['title'],
        'author_id': music_list['owner_id'],
        'author_name': music_list['owner_nickname'],
        'duration': music_list['duration'],
        'user_count': music_list['user_count'],
        'play_url': music_list['play_url']['uri'],
    }
    videos = []
    aweme_ids = []
    for aweme in aweme_list:
        video = {
            'user_id': str(aweme['author_user_id']),
            'video_id': str(aweme['aweme_id']),
            'cover': aweme['video']['cover']['url_list'][0],
            'description': aweme['desc'],
            'comment_count': aweme['statistics']['comment_count'],
            'share_count': aweme['statistics']['share_count'],
            'like_count': aweme['statistics']['digg_count'],
            'video_create_time': datetime.datetime.fromtimestamp(aweme['create_time']),
            'share_url': aweme['share_info']['share_url']
        }
        for play_url in aweme['video']['play_addr']['url_list']:
            if play_url.find('aweme.snssdk') > 0:
                video['play_url'] = play_url
                break
        videos.append(video)
        aweme_ids.append(video['video_id'])
    music_cleared['aweme_list'] = aweme_ids

    DYV_MUL.add_all(videos)
    DouYinMusic.add_with_conflict(**music_cleared)
#
#
# def douyin_music_fresh():
#     pass

routing_tasks = {
    'douyin.author.post': douyin_author_post,
    'douyin.author.feed': douyin_author_feed,
    'douyin.author.following': douyin_author_following,
    'douyin.author.follower': douyin_author_follower,
    'douyin.author.info': douyin_author_info,
    'douyin.author.favorite': douyin_author_favorite,
    'douyin.author.comment': douyin_author_comment,
    'douyin.author.music.detail': douyin_music_detail,
    # 'douyin.author.music.hot': douyin_music_hot,
    # 'douyin.author.music.fresh': douyin_music_fresh,
    'douyin.author.category': douyin_category
}

# channel.queue_bind(exchange="DouYin", queue="douyin.author", routing_key='douyin.author.#',)


def cb(ch, method, properties, body):
    # print(" [x] %r:%r" % (method.routing_key, body))
    task = routing_tasks.get(method.routing_key, None)
    r = ''
    if task and callable(task):
        try:
            r = task(json.loads(body.decode('utf-8')))
        except (KeyError, IndexError, JSONDecodeError, UnicodeEncodeError):
            # 这些报错说明都因返回的数据格式不对，可以直接抛弃
            print("error", body)
            traceback.print_exc()

            r = "OK"
    elif not task:
        r = 'OK'
    if r == 'OK':
        ch.basic_ack(delivery_tag=method.delivery_tag)



channel.basic_qos(prefetch_count=50)
channel.basic_consume(cb, queue="douyin.author")

channel.start_consuming()
