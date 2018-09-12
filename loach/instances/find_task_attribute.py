# -*- coding: utf-8 -*-

"""
脚本 用来临时分发搜索任务

"""
import json
import requests
import pandas
# from loach.model.douyinaccount import DouYinAccount

# sql = 'SELECT short_id from :t_name ORDER BY follower_num DESC LIMIT 10000;'

# r = DouYinAccount.execute('select', sql)
# r = pandas.read_excel('../../opt/sql.xlsx')
# headers = {"Content-Type": "application/x-www-form-urlencoded"}
# body = []
# for index, row in r.iterrows():
#     if pandas.isnull(row['short_id']):
#         continue
#     task = {
#         'short_id': str(row['short_id']),
#         'attrs': ["follower"]
#     }
#     body.append(task)
# print(len(body))
#
# res = requests.post('http://192.168.1.100:8080/douyin/task/searches/', data=json.dumps(body))
#
# if res.status_code == 200:
#     print(res.text)
# else:
#     print(res.status_code)

def kol_letter():
    import xlrd
    msg = '哈喽～你好！我们是家品牌代理公司，觉得您在抖音的视频内容还挺适合做品牌商务合作的，是否方便给到您的联系方式或者添加我的微信号（xxx）-备注“抖音合作”，我们简单沟通下^_^'
    book = xlrd.open_workbook('/Users/apple/Desktop/task/1000-2000名单.xlsx')
    sheet = book.sheet_by_index(0)
    cols = sheet.col_values(1, start_rowx=1)
    print(cols)
    task = []
    for short_id in cols:
        item = {
            "short_id": short_id,
            "words": msg
        }
        task.append(item)
    while task[10:]:
        requests.post("http://192.168.1.100:8080/douyin/task/kol_letter/", data=json.dumps(task[:10]))
        print(task[:10])
        task = task[10:]


if __name__ == '__main__':
    kol_letter()