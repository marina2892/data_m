from scrapy.loader import ItemLoader
from .items import GbAutoYoulaItem
from .items import GbHhItem
from .items import GbHh_companyItem
from .items import GbInst_tagItem
from .items import GbInst_postItem
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy import Selector



def get_parameters(item):
    selector = Selector(text = item)
    data = {
        'name':selector.xpath("//div[contains(@class,'AdvertSpecs_label')]/text()").extract_first(),
        'value':selector.xpath("//div[contains(@class,'AdvertSpecs_data')]//text()").extract_first()
    }
    return data

def get_description(item):
    selector = Selector(text = item)
    descr = selector.xpath("//div[@class='g-user-content']//text()").extract()
    if not descr:
        descr = selector.xpath("//div[@itemprop='description']//text()").extract()
    return descr

def get_field_activity(item):
    return item.split(',')
    

class AutoyoulaLoader(ItemLoader):
    default_item_class = GbAutoYoulaItem
    url_out = TakeFirst() 
    title_out = TakeFirst()
    parameters_in = MapCompose(get_parameters) 
    
class HhLoader(ItemLoader):
    default_item_class = GbHhItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = Join()
    salary_out = TakeFirst()
    description1_in = Join()
    description1_out = TakeFirst()
    description2_in = MapCompose(get_description)
    description2_out = Join()
    url_company_out = TakeFirst()
    
class Hh_companyLoader(ItemLoader):
    default_item_class = GbHh_companyItem
    company_name_in = Join()
    company_name_out = TakeFirst()
    company_url_out = TakeFirst()
    field_activity_in = Join()
    field_activity_out = MapCompose(get_field_activity)
    company_description_in = Join()
    company_description_out = TakeFirst()
    
class Inst_tagLoader(ItemLoader):
    default_item_class = GbInst_tagItem
    date_parse_out = TakeFirst()
    tag_name_out = TakeFirst()
    tag_url_out = TakeFirst()
    
class Inst_postLoader(ItemLoader):
    default_item_class = GbInst_postItem
    date_parse_out = TakeFirst()
    post_text_out = TakeFirst()