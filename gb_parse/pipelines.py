# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import pymongo

class GbParsePipeline:
    def process_item(self, item, spider):
        return item
    
class GbParseMongoPipeline:
    def __init__(self):
        client = pymongo.MongoClient() 
        #self.db = client['autoyoula']
        #self.db = client['hh']
        self.db = client['inst']
        

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item    
    
class GbImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['post_img']: 
            try:
                yield Request(url)
            except Exception as e:
                print(e)
     
     def item_completed(self, results, item, info):
        if results:
            item['post_img'] = [itm[1] for itm in results]
        return item