# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from items import PornVideoItem
from hashlib import md5, sha1
import MySQLdb


class PornhubMysqlDBPipeline(object):
    def __init__(self):
        ## IP 用户名 密码 数据库
        self.db = MySQLdb.connect("localhost", "root", "root", "blue_sender")
        self.cursor = self.db.cursor()
        # if your existing DB has duplicate records, refer to:
        # https://stackoverflow.com/questions/35707496/remove-duplicate-in-mongodb/35711737

    def process_item(self, item, spider):
        # print 'MongoDBItem', item
        """ 判断类型 存入MongoDB """
        if isinstance(item, PornVideoItem):
            if not item['exists']:
                sha1_object = sha1()
                sha1_object.update(item['quality_480p'])
                sql = "INSERT INTO bs_porn_data(f_sha1," \
                      "f_video_price," \
                      "f_video_title," \
                      "f_video_duration," \
                      "f_image_url," \
                      "f_video_src_page," \
                      "f_video_src_url," \
                      "f_image_file_path," \
                      "f_video_file_path," \
                      "f_status) VALUE ('%s','%d','%s','%d','%s','%s','%s','%s','%s','%d')" % \
                      (sha1_object.hexdigest(), 990, item['video_title'],
                       int(item['video_duration'].encode("utf-8")),
                      item['image_url'], item['link_url'],item['quality_480p'],
                       item['image_file_path'], item['video_file_path'], 2)
                try:
                    self.cursor.execute(sql)
                    self.db.commit()
                except:
                    self.db.rollback()
                    pass
        return item

    def __del__(self):
        self.cursor.close()
        self.db.close()
