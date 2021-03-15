# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class GbAutoYoulaItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    list_img = scrapy.Field()
    parameters = scrapy.Field()
    description = scrapy.Field()
    user_url = scrapy.Field()

class GbHhItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description1 = scrapy.Field()
    description2 = scrapy.Field()
    skills = scrapy.Field()
    url_company = scrapy.Field()

class GbHh_companyItem(scrapy.Item): 
    _id = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    field_activity = scrapy.Field()
    company_description = scrapy.Field()
    
class GbInst_tagItem(scrapy.Item): 
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    tag_name = scrapy.Field()
    tag_url = scrapy.Field()
    
class GbInst_postItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    post_text = scrapy.Field()
    post_img = scrapy.Field()
    