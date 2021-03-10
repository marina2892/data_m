import requests
import pymongo
import bs4
from urllib.parse import urljoin

class MagnitParse:
    def __init__(self, url, db_client):
        self.url = url
        self.db = db_client['magnit']
        self.collection = self.db['promo']
        
    def _get_response(self, url):
        return requests.get(url)
    
    def _get_soup(self, url):
        response = self._get_response(url)
        return bs4.BeautifulSoup(response.text, 'lxml')
    
    
    @staticmethod
    def get_price(a, div):
        integer = a.find('div', attrs = {'class': div}).find('span', attrs = {'class': 'label__price-integer'}).text
        decimal = a.find('div', attrs = {'class': div}).find('span', attrs = {'class': 'label__price-decimal'}).text
        return f'{integer}.{decimal}'
   
    @staticmethod
    def get_date(dates, n):
        months = {'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'май': '05', 'июн': '06', 'июл': '07', 'авг': '08', 'сент': '09', 'окт': '10', 'ноя': '11', 'дек': '12'}
        d = dates.find_all('p', recursive = False)
        if len(d) == 1:
            n = 0
        list_d = d[n].text.split()
        day = list_d[1]
        month = months[list_d[2][:3]]
        return f'2021-{month}-{day}'
        
    def _get_template(self):
        return {
            'url': lambda a: urljoin(self.url, a.attrs.get('href', '')),
            'promo_name': lambda a: a.find('div', attrs = {'class': 'card-sale__name'}).text,
            'product_name': lambda a:a.find('div', attrs = {'class': 'card-sale__title'}).text,
            'old_price': lambda a: self.get_price(a, div = 'label__price label__price_old'),
            'new_price': lambda a: self.get_price(a, div = 'label__price label__price_new'),
            'image_url':lambda a: urljoin('https://magnit.ru/', a.find('img', attrs = {'class': 'lazy'}).attrs.get('data-src', '')),
            'date_from':lambda a: self.get_date(a.find('div', attrs = {'class': 'card-sale__date'}), n = 0),
            'date_to':lambda a: self.get_date(a.find('div', attrs = {'class': 'card-sale__date'}), n = 1)
        }    
    
    def _parse(self, prod_a):
        data = {}
        for key, func in self._get_template().items():
            try:
                data[key] = func(prod_a)
            except AttributeError:
                pass
            
        return data
      
    def _save(self, dict_prod):
        self.collection.insert_one(dict_prod)
          
        
        
    def run(self):
        soup = self._get_soup(self.url)
        catalog = soup.find('div', attrs = {'class':'сatalogue__main'})
        for prod_a in catalog.find_all('a', recursive = False):
            dict_prod = self._parse(prod_a)
            self._save(dict_prod)
    
url = 'https://magnit.ru/promo/?geo=moskva'
db_client = pymongo.MongoClient('mongodb://localhost:27017')
parser = MagnitParse(url, db_client)
parser.run()