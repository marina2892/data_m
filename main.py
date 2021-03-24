import os # чтобы обращаться к переменым окружения
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider
from processing_data import Tasks


if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    crawler_settings = Settings()
    init_task = Tasks('putvlputin','marinaterekhina92')
    inst_users = init_task.start_users


    crawler_settings.setmodule('gb_parse.settings')
    crawler_proc = CrawlerProcess(settings=crawler_settings)

    crawler_proc.crawl(InstagramSpider, login = os.getenv('INST_LOGIN'), password = os.getenv('INST_PASSWORD'), inst_users = inst_users, tasks = init_task)
    crawler_proc.start()

