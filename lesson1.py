import requests
from pathlib import Path
import time
import json

class Parser:
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'}
    
    def __init__(self, url_categories, url_products, save_path):
        
        self.url_categories = url_categories
        self.url_products = url_products
        self.save_path = save_path
    
    def _get_response(self, url, params):
        while 1:
            response = requests.get(url, params = params, headers = self.__class__.headers)
            if response.status_code == 200:
                return response
            else:
                time.sleep(0.5)
                
    def _get_products(self, url_new_page):
        response_products = self._get_response(url_new_page, None)
        products = response_products.json()  
        return products
        
    
    def _get_product(self, category_code):
        url = self.url_products
        while (url):
            if (url == self.url_products):
                params = {'store':None,'records_per_page':12,'page':1,'categories':category_code,'ordering':None,'price_promo__gte':None,'price_promo__lte':None,'search':None}
                response_products = self._get_response(self.url_products, params)
                products = response_products.json()
                url = products['next']
                for product in products['results']: 
                    yield product 
            else:
                products = self._get_products(url)
                url = products['next']
                for product in products['results']:
                    yield product
       
    def run(self):
        data = {}
        response_category = self._get_response(self.url_categories, None)
        list_category = response_category.json()
        
        for category in list_category:
            list_products = []
            
            for product in self._get_product(category['parent_group_code']):
                list_products.append(product)    
            
            data.update(category)
            data.update({'products':list_products})
            product_path = self.save_path.joinpath(f"{category['parent_group_name']}.json")
            product_path.write_text(json.dumps(data, ensure_ascii = False))           
          
          
save_path = Path(__file__).parent.joinpath('categories')
if not save_path.exists():
    save_path.mkdir()
parser = Parser('https://5ka.ru/api/v2/categories/', 'https://5ka.ru/api/v2/special_offers/', save_path)
parser.run()