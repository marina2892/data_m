import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    crawler_settings = Settings()
    inst_users = ['_agentgirl_']
    crawler_settings.setmodule('gb_parse.settings')
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    crawler_proc.crawl(InstagramSpider, login = os.getenv('INST_LOGIN'), password = os.getenv('INST_PASSWORD'), inst_users = inst_users)
    crawler_proc.start()