import scrapy
from ..loaders import HhLoader
from ..loaders import Hh_companyLoader

class HhRuSpider(scrapy.Spider):
    name = 'hh_ru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://barnaul.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=11']
    
    _vacancy_xpath = {
        'vacancy':"//a[@data-qa = 'vacancy-serp__vacancy-title']/@href",
        'pagination':"//a[@data-qa = 'pager-page']/@href",
        'url_company':"//a[@class = 'vacancy-company-name']/@href"
     }
    _vacancy_xpath_loader = {
        'title':"//h1[@data-qa = 'vacancy-title']//text()",
        'salary':"//p[@class = 'vacancy-salary']//text()",
        'description1':"//div[@class = 'vacancy-description']//div[contains(@class,'bloko-gap')]//text()",
        'description2':"//div[@class = 'vacancy-description']",
        'skills':"//div[@class = 'bloko-tag-list']//div[contains(@class,'bloko-tag')]//text()",
     }
    
    _company_xpath = {
        'company_name':"//div[@class = 'company-header']//span[@class = 'company-header-title-name']/text()",
        'company_url':"//a[@class = 'g-user-content']/@href",
        'field_activity':"//div[@class = 'employer-sidebar-block']/p/text()",
        'company_description':"//div[@class = 'g-user-content']//text()"
    
    
    }
    
    def _get_follow(self, response, selector_str, callback, **kwargs):
        for a in response.xpath(selector_str):
            yield response.follow(a, callback = callback, cb_kwargs = kwargs)
            
            
    def parse(self, response, *args, **kwargs):
        if not kwargs:
            yield from self._get_follow(response, self._vacancy_xpath['pagination'], self.parse)
            yield from self._get_follow(response, self._vacancy_xpath['vacancy'], self.vac_parse)
        else:
            yield from self._get_follow(response, self._vacancy_xpath['pagination'], self.parse, kwargs)
            yield from self._get_follow(response, self._vacancy_xpath['vacancy'], self.vac_parse, kwargs)
        
    def vac_parse(self, response, **kwargs):
        loader = HhLoader(response=response)
        loader.add_value('url', response.url)
        url_company = response.xpath(self._vacancy_xpath['url_company']).extract_first()
        loader.add_value('url_company', response.urljoin(url_company))
        for key, value in self._vacancy_xpath_loader.items():
            loader.add_xpath(key, value)
        yield loader.load_item()
        if not kwargs:     
            yield response.follow(response.urljoin(url_company), callback = self.company_parse) 
        
    def company_parse(self, response):
        loader = Hh_companyLoader(response=response)
        for key, value in self._company_xpath.items():
            loader.add_xpath(key, value)        
        yield loader.load_item()
        link_company_vac = response.xpath("//a[@data-qa = 'employer-page__employer-vacancies-link']/@href").extract_first()
        yield response.follow(response.urljoin(link_company_vac), callback = self.parse, cb_kwargs = {'company':0})
        
        
    
         
        
       
        
    
        
           