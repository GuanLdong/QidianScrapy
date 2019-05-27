# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QidianscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    collection = table = 'Qidian'
    # Author of novle
    Author = scrapy.Field()
    # title of novle
    Title = scrapy.Field()
    # Request url
    Url = scrapy.Field()
    # breief instruction
    Content = scrapy.Field()
    # main class
    FictionClass1 = scrapy.Field()
    # second class
    FictionClass2 = scrapy.Field()
    # Serialization status
    State = scrapy.Field()
    # word number
    Number = scrapy.Field()