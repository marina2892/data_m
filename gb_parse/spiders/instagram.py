import scrapy
import json
from ..loaders import SubscriptionsLoader
from ..loaders import SubscribersLoader



class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'

    def __init__(self, login, password, inst_users, *args, **kwargs):
        self.login = login
        self.password = password
        self.inst_users = inst_users
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
            for user_name in self.inst_users:
                self.current_user = user_name
                yield response.follow(f'https://www.instagram.com/{user_name}/?__a=1', callback = self.get_user_id)

            
    def get_user_id(self, response):
        new_page = response.json()
        user_id = new_page['graphql']['user']['id']

        yield response.follow(f"/graphql/query/?query_hash=3dec7e2c57367ef3da3d987d89f9dbc8&variables={{\"id\":\"{user_id}\",\"include_reel\":true,\"fetch_mutual\":false,\"first\":24}}", callback=self.user_subscriptions,cb_kwargs = {'user_id':user_id})
        yield response.follow(
            f"/graphql/query/?query_hash=5aefa9893005572d237da5068082d8d5&variables={{\"id\":\"{user_id}\",\"include_reel\":true,\"fetch_mutual\":false,\"first\":24}}",
            callback=self.user_subscribers, cb_kwargs={'user_id': user_id})

    def user_subscriptions(self, response, **kwargs):
        jpage = response.json()

        for subscription_name in jpage['data']['user']['edge_follow']['edges']:
            loader = SubscriptionsLoader(response=response)
            loader.add_value('user', self.current_user)
            loader.add_value('url_subcription', f"https://www.instagram.com/{subscription_name['node']['username']}")
            yield loader.load_item()
        next_page = jpage['data']['user']['edge_follow']['page_info']['end_cursor']
        if next_page:
            yield response.follow(
                f"/graphql/query/?query_hash=3dec7e2c57367ef3da3d987d89f9dbc8&variables={{\"id\":\"{kwargs['user_id']}\",\"include_reel\":true,\"fetch_mutual\":false,\"first\":24,\"after\":\"{next_page}\"}}",
                callback=self.user_subscriptions, cb_kwargs = {'user_id':kwargs['user_id']})


    def user_subscribers(self, response, **kwargs):
        jpage = response.json()

        for subscriber_name in jpage['data']['user']['edge_followed_by']['edges']:
            loader = SubscribersLoader(response=response)
            loader.add_value('user', self.current_user)
            loader.add_value('url_subcriber', f"https://www.instagram.com/{subscriber_name['node']['username']}")
            yield loader.load_item()
        next_page = jpage['data']['user']['edge_followed_by']['page_info']['end_cursor']
        if next_page:
            yield response.follow(
                f"/graphql/query/?query_hash=5aefa9893005572d237da5068082d8d5&variables={{\"id\":\"{kwargs['user_id']}\",\"include_reel\":true,\"fetch_mutual\":false,\"first\":24,\"after\":\"{next_page}\"}}",
                callback=self.user_subscribers, cb_kwargs = {'user_id':kwargs['user_id']})


    def js_data_extract(self, response):
        script = response.xpath("//script[contains(text(), 'window._sharedData =')]/text()").extract_first()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])
