from scrapy.loader import ItemLoader
from .items import SubscriptionsItem
from .items import SubscribersItem
from itemloaders.processors import TakeFirst


class SubscriptionsLoader(ItemLoader):
    default_item_class = SubscriptionsItem
    user_out = TakeFirst()
    url_subcription_out = TakeFirst()

class SubscribersLoader(ItemLoader):
    default_item_class = SubscribersItem
    user_out = TakeFirst()
    url_subcriber_out = TakeFirst()