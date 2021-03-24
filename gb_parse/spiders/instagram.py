import scrapy
import json
from ..loaders import SubscriptionsLoader




class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'

    

    def __init__(self, login, password, inst_users, tasks, *args, **kwargs):
        self.login = login
        self.password = password
        self.inst_users = inst_users
        self.tasks = tasks
        self.start_count = 0

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
                yield response.follow(f'https://www.instagram.com/{user_name}/?__a=1', callback = self.get_user_id, cb_kwargs={'user_name':user_name})

            
    def get_user_id(self, response, **kwargs):
        new_page = response.json()
        user_id = new_page['graphql']['user']['id']
        yield response.follow(f"/graphql/query/?query_hash=3dec7e2c57367ef3da3d987d89f9dbc8&variables={{\"id\":\"{user_id}\",\"include_reel\":true,\"fetch_mutual\":false,\"first\":24}}", callback=self.user_subscriptions,cb_kwargs = {'user_id':user_id, 'user_name':kwargs['user_name'] })



    def user_subscriptions(self, response, **kwargs):
        jpage = response.json()

        for subscription_name in jpage['data']['user']['edge_follow']['edges']:
            loader = SubscriptionsLoader(response=response)
            loader.add_value('user', kwargs['user_name'])
            loader.add_value('subscription', subscription_name['node']['username'])
            yield loader.load_item()
        next_page = jpage['data']['user']['edge_follow']['page_info']['end_cursor']
        if next_page:
            yield response.follow(
                f"/graphql/query/?query_hash=3dec7e2c57367ef3da3d987d89f9dbc8&variables={{\"id\":\"{kwargs['user_id']}\",\"include_reel\":true,\"fetch_mutual\":false,\"first\":24,\"after\":\"{next_page}\"}}",
                callback=self.user_subscriptions, cb_kwargs = {'user_id':kwargs['user_id'],'user_name':kwargs['user_name']})
        else:
            if self.start_count == 2:
                self.check_result = self.tasks.check_rel()
                if self.check_result == 0:
                    self.iter = next(self.start_result)
                    if self.iter == 0:
                        print(f"связь {self.tasks.start_users[0]}-{self.tasks.start_users[1]} установить невозможно")
                        self.crawler.stop()
                    else:
                        yield response.follow(f'https://www.instagram.com/{self.iter}/?__a=1', callback=self.get_user_id,
                                          cb_kwargs={'user_name': self.iter})
                else:
                    print(f"связь {self.check_result} подтверждена")
                    self.crawler.stop()

            else:
                self.start_count+=1
                if (self.start_count == 2):
                    self.start_result = self.tasks.check_start_rel()
                    if not (isinstance(self.start_result, int)):
                        self.iter = next(self.start_result)
                        yield response.follow(f'https://www.instagram.com/{self.iter}/?__a=1', callback=self.get_user_id,
                                              cb_kwargs={'user_name': self.iter})

                    elif self.start_result == 0:
                        print(f"связь {self.tasks.start_users[0]}-{self.tasks.start_users[1]} установить невозможно")
                        self.crawler.stop()
                    else:
                        print(f"связь {self.tasks.start_users[0]}-{self.tasks.start_users[1]} подтверждена")
                        self.crawler.stop()


    def js_data_extract(self, response):
        script = response.xpath("//script[contains(text(), 'window._sharedData =')]/text()").extract_first()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])
