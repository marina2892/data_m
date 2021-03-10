import scrapy
import re
import pymongo

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru'] 
    start_urls = ['https://auto.youla.ru/']  
    _css_selectors = {
        'brands':'.TransportMainFilters_brandsList__2tIkv .ColumnItemList_container__5gTrc a.blackLink',
        'pagination':'a.Paginator_button__u1e7D',
        'car':'.SerpSnippet_titleWrapper__38bZM a.SerpSnippet_name__3F7Yu'    
    }
    
    db_client = pymongo.MongoClient('mongodb://localhost:27017')
    db = db_client['autoyoula']
    collection = db['cars']    
    
    @staticmethod
    def get_user(response):
        marker = "window.transitState = decodeURIComponent"
        for script in response.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return (response.urljoin(f"/user/{result[0]}")) if result else None
            except TypeError:
                pass        
        
    
    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            link = a.attrib.get('href')
            yield response.follow(link, callback = callback, cb_kwargs = kwargs)
        
        
    def parse(self, response, *args, **kwargs):
        brands = response.css(self._css_selectors['brands'])
        yield from self._get_follow(response,self._css_selectors['brands'], self.brand_parse, hello = 'moto') 
    
        
            
    def brand_parse(self, response, **kwargs):
        yield from self._get_follow(response, self._css_selectors['pagination'],self.brand_parse)
        yield from self._get_follow(response, self._css_selectors['car'], self.car_parse)    
        
            
    def car_parse(self, response):
        dict_param = {}
        for parameter in response.css('.AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX'):
            name = parameter.css('.AdvertSpecs_label__2JHnS::text').extract()
            if parameter.css('.AdvertSpecs_data__xK2Qx a.blackLink'):
                value = parameter.css('.AdvertSpecs_data__xK2Qx a.blackLink::text').extract()
            else:
                value = parameter.css('.AdvertSpecs_data__xK2Qx::text').extract()
            dict_param.update({''.join(name):''.join(value)})        
        
        data = {
            'title':response.css('.AdvertCard_advertTitle__1S1Ak::text').extract_first(),
            'list_img':[a.attrib.get('src') for a in response.css('.PhotoGallery_photoWrapper__3m7yM img.PhotoGallery_photoImage__2mHGn')],
            'parameters':dict_param,
            'description':response.css('.AdvertCard_descriptionInner__KnuRi::text').extract_first(),
            'user_url':AutoyoulaSpider.get_user(response)
        }
        
        self.save(data)
        
    def save(self, data):
        AutoyoulaSpider.collection.insert_one(data)
        
        
           
        
        
        
        
