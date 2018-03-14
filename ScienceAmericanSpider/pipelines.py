# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

from scrapy import crawler


class ScienceamericanspiderPipeline(object):
    def __init__(self,vDBPath):
        self.dbPath=vDBPath

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            vDBPath=crawler.settings.get('DBPATH')
        )

    def open_spider(self,spider):
        self.db=sqlite3.connect(self.dbPath)

    def close_spider(self,spider):
        self.db.close()

    def process_item(self, item, spider):
        if item['fileType']=='podcast':
            if self.db.execute("select * from article where title=?",(item['name'],)).fetchone() is None:
                self.db.execute("insert into article (title,description,text,url,fileType,category,podcast) "
                                "VALUES (?,?,?,?,?,?,?)"
                                ,(item['name'],item['description'],item['text']
                                  ,item['url'],item['fileType'],item['category']
                                  ,item['podcast']))
        elif item['fileType']=='article':
            if self.db.execute("select * from article where title=?",(item['name'],)).fetchone() is None:
                self.db.execute("insert into article (title,description,text,url,fileType,category) VALUES (?,?,?,?,?,?)"
                            ,(item['name'],item['description'],item['text']
                              ,item['url'],item['fileType'],item['category']))
        self.db.commit()
        return item
