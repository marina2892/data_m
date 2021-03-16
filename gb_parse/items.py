# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



class SubscriptionsItem(scrapy.Item):
    _id = scrapy.Field()
    user = scrapy.Field()
    url_subcription = scrapy.Field()

class SubscribersItem(scrapy.Item):
    _id = scrapy.Field()
    user = scrapy.Field()
    url_subcriber = scrapy.Field()


    