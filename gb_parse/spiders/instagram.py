import scrapy
import json
from datetime import datetime
from ..loaders import Inst_tagLoader
from ..loaders import Inst_postLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    _tags_path = '/explore/tags/'
    

    def __init__(self, login, password, tags, *args, **kwargs):
        self.login = login
        self.password = password
        self.tags = tags
        super().__init__(*args, **kwargs)

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url, method = 'POST', 
                callback = self.parse, 
                formdata = {
                    'username': self.login, 
                    'enc_password': self.password
                    }, 
                headers = {'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            print(e)
            for tag_name in self.tags:
                yield response.follow(f'{self._tags_path}{tag_name}/', callback = self.tag_page_parse)
            
    def tag_page_parse(self, response):
        js_data = self.js_data_extract(response)
        loader = Inst_tagLoader(response=response)
        tag_name = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']['name']
        tag_url = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']['profile_pic_url']
        
        loader.add_value('date_parse', str(datetime.today()))
        loader.add_value('tag_name', tag_name)
        loader.add_value('tag_url', tag_url)
        
        yield loader.load_item()
        
        for post in js_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
            post_text = ''
            try:
                post_text = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
            except Exception:
                pass
            post_img = post['node']['display_url']
            
            loader = Inst_postLoader(response=response)
            loader.add_value('date_parse', str(datetime.today()))
            loader.add_value('post_text', post_text)
            loader.add_value('post_img', post_img)
            yield loader.load_item()
        
        next_page = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        url_next = self.get_next_url('9b498c08113f1e09617a1703c22b2f32', next_page)
        yield response.follow(url_next, callback=self.page_parse)



    def page_parse(self, response):
        new_page = response.json()
        for post in new_page['data']['hashtag']['edge_hashtag_to_media']['edges']:
            post_text = ''
            try:
                post_text = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
            except Exception:
                pass
            post_img = post['node']['display_url']
            loader = Inst_postLoader(response=response)
            loader.add_value('date_parse', str(datetime.today()))
            loader.add_value('post_text', post_text)
            loader.add_value('post_img', post_img)
            yield loader.load_item()            
            
        next_page = new_page['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        if next_page:
            url_next = self.get_next_url('9b498c08113f1e09617a1703c22b2f32',next_page)
            yield response.follow(url_next, callback=self.page_parse)        
        

    def js_data_extract(self, response):
        script = response.xpath("//script[contains(text(), 'window._sharedData =')]/text()").extract_first()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])
    
    
        
    def get_next_url(self, hash_str, next_page):
        return f"https://www.instagram.com/graphql/query/?query_hash={hash_str}&variables={{\"tag_name\":\"python\",\"first\":7,\"after\":\"{next_page}\"}}"
        