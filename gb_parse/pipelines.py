# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

class GbParsePipeline:
    def process_item(self, item, spider):
        return item
    
class GbParseMongoPipeline:
    def __init__(self):
        client = pymongo.MongoClient() #не указываем строку для подключения, по default-у он коннектится к локальной базе данных
        #self.db = client['autoyoula']
        self.db = client['hh']

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item    