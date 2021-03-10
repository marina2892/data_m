import requests
import bs4
from urllib.parse import urljoin
import datetime
from db.db import Database

class GBParse:
    def __init__(self, url, db):
        self.url = url
        self.db = db
        self.done_urls = set()
        self.tasks = [self._get_task(self.url, self._parse_feed)]
        
        self.done_urls.add(self.url)
        
    @staticmethod
    def get_date(date):
        months = {'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'мая': '05', 'июн': '06', 'июл': '07', 'авг': '08', 'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'}
        
        list_d = date.split()
        day = list_d[0]
        month = months[list_d[1][:3]]
        year = list_d[2]
        
        return datetime.date(int(year), int(month), int(day))  
        
        
    def _get_task(self, url, callback):
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)
        return task
        
       
    def _get_soup(self, url):
        return bs4.BeautifulSoup(self._get_response(url).text, 'lxml')
    
    def _get_response(self, url):
        return requests.get(url)
    
    def _parse_post(self, url, soup):
        
        comments_id = soup.find('comments').get('commentable-id')
        comments = requests.get(f"https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id={str(comments_id)}&order=desc").json()
        if comments:
            comments_list = [{'auth': comment.get('comment').get('user').get('full_name'), 'text': comment.get('comment').get('body')} for comment in comments]
        else:
            comments_list = []
        data = {
            'post_data':{
                'url':url,
                'title':soup.find('h1', attrs = {'class': 'blogpost-title'}).text,
                'url_img':soup.find('div', attrs = {'itemprop':'image'}).text,
                'date':str(self.get_date(soup.find('time', attrs = {'itemprop':'datePublished'}).text))
            },
            'writer_data':{
                'url':urljoin(url, soup.find('div', attrs = {'itemprop':'author'}).parent.attrs.get('href')),
                'name':soup.find('div', attrs = {'itemprop':'author'}).text
            },
            'tags_data':[{'name':tag.text,'url':urljoin(self.url, tag.attrs.get('href'))} for tag in soup.find_all('a', attrs = {'class': 'small'})],
            
            'comments': comments_list
        }
        return data
        
    def _parse_feed(self, url, soup):
        ul = soup.find('ul', attrs = {'class':'gb__pagination'})
        pag_urls = set(urljoin(url, link.attrs.get('href')) for link in ul.find_all('a') if link.attrs.get('href'))
        for pag_url in pag_urls:
            if pag_url not in self.done_urls:
                self.tasks.append(self._get_task(pag_url, self._parse_feed))
                self.done_urls.add(pag_url)
        
        post_items = soup.find('div', attrs = {'class':'post-items-wrapper'})
        posts_urls = set(urljoin(url, link.attrs.get('href')) for link in post_items.find_all('a', attrs = {'class': 'post-item__title'}) if link.attrs.get('href'))        
        for post_urls in posts_urls:
            if post_urls not in self.done_urls:
                self.tasks.append(self._get_task(post_urls, self._parse_post))
                self.done_urls.add(post_urls)
                
    def _save(self, data):
        self.db.create_post(data)    
        
        
    def run(self):
        for task in self.tasks:
            task_result = task()
            if task_result:
                self._save(task_result)
                
                
if __name__ == '__main__':
    database = Database('sqlite:///gb_blog.db')
    parser = GBParse('https://geekbrains.ru/posts', database)
    parser.run()