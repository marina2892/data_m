from scrapy.loader import ItemLoader
from .items import SubscriptionsItem
from itemloaders.processors import TakeFirst


class SubscriptionsLoader(ItemLoader):
    default_item_class = SubscriptionsItem
    user_out = TakeFirst()
    subscription_out = TakeFirst()

