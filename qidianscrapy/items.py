# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QidianscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    collection = table = 'Qidian'
    Author = scrapy.Field()
    Title = scrapy.Field()
    Url = scrapy.Field()
    Content = scrapy.Field()
    FictionClass1 = scrapy.Field()
    FictionClass2 = scrapy.Field()
    State = scrapy.Field()
    Number = scrapy.Field()