import scrapy
import re
from ..loaders import AutoyoulaLoader

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru'] #регламентирует, на какие домены паук будет переходить
    start_urls = ['https://auto.youla.ru/']  #список точек входа на сайт
    _xpath_selectors = {
        'brands':"//div[@data-target='transport-main-filters']/div[contains(@class,'TransportMainFilters_brandsList')]//a[@data-target='brand']/@href",
        'pagination':"//a[contains(@class,'Paginator_button')]/@href",
        'car':"//div[contains(@class,'SerpSnippet_titleWrapper')]//a[@data-target='serp-snippet-title']/@href"   
    
    }
    
     
    
    @staticmethod
    def get_user(response):
        marker = "window.transitState = decodeURIComponent"
        for script in response.xpath("//script"):
            try:
                if marker in script.xpath("./text()").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.xpath("./text()").extract_first())
                    return (response.urljoin(f"/user/{result[0]}")) if result else None
            except TypeError:
                pass        
        
    
    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.xpath(select_str):
            yield response.follow(a, callback = callback, cb_kwargs = kwargs)
        
        
    def parse(self, response, *args, **kwargs):
        
        
        yield from self._get_follow(response,self._xpath_selectors['brands'], self.brand_parse, hello = 'moto') 
    
        
            
            
    def brand_parse(self, response, **kwargs):
        yield from self._get_follow(response, self._xpath_selectors['pagination'],self.brand_parse)
        
        
        
        yield from self._get_follow(response, self._xpath_selectors['car'], self.car_parse)    
        
            
    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value('url', response.url)
        a=9
        
        dict_param = {}
        for parameter in response.xpath("//div[contains(@class,'AdvertSpecs_label')]"):
            name = parameter.xpath("./text()").extract()
            if parameter.xpath("../div[contains(@class,'AdvertSpecs_data')]/a"):
                value = parameter.xpath("../div[contains(@class,'AdvertSpecs_data')]/a/text()").extract()
            else:
                value = parameter.xpath("../div[contains(@class,'AdvertSpecs_data')]/text()").extract()   
            dict_param.update({''.join(name):''.join(value)})
        
            
        
       
        
        data = {
            'title':response.xpath("//div[@data-target='advert-title']/text()").extract_first(),
            'list_img':[a for a in response.xpath("//img[contains(@class,'PhotoGallery_photoImage')]/@src").extract()],
            'parameters':dict_param,
            'description':response.xpath("//div[contains(@class,'AdvertCard_descriptionInner')]/text()").extract_first(),
            'user_url':AutoyoulaSpider.get_user(response)
        }
        
        
        yield data
        
       
       
        
       
        
   
        
        
           
        
        
        
        
