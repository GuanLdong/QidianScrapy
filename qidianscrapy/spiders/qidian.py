# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider,Request
from qidianscrapy.items import QidianscrapyItem
from pyquery import PyQuery as pq
from io import BytesIO
from fontTools.ttLib import TTFont
import requests
import re

class QidianSpider(scrapy.Spider):
    name = 'qidian'
    allowed_domains = ['qidian.com']
    def __init__(self):
        self.start_urls = 'http://a.qidian.com/?page='

    def get_font(self,url):
        response = requests.get(url)
        font = TTFont(BytesIO(response.content))
        cmap = font.getBestCmap()
        font.close()
        return cmap

    def get_encode(self,cmap,values):
        WORD_MAP = {'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6',
                    'seven': '7', 'eight': '8', 'nine': '9', 'period': '.'}
        word_count = ''
        for value in values.split(';'):
            value = value[2:]
            key = cmap[int(value)]
            word_count += WORD_MAP[key]
        return word_count

    def start_requests(self):
        for page in range(1,self.settings.get('MAX_PAGE')+1):
            url = self.start_urls+str(page)
            yield Request(url,self.parse)

    def parse(self, response):

        doc = pq(response.text)
        # 获取当前字体文件名称
        classattr = doc('p.update > span > span').attr('class')
        pattern = '</style><span.*?%s.*?>(.*?)</span>' % classattr
        # 获取当前页面所有被字数字符
        numberlist = re.findall(pattern, response.text)
        fonturl = doc('p.update > span > style').text()
        # 通过正则获取当前页面字体文件链接
        url = re.search('woff.*?url.*?\'(.+?)\'.*?truetype', fonturl).group(1)
        cmap = self.get_font(url)

        quotes = response.xpath('/html/body/div[2]/div[5]/div[2]/div[2]/div/ul/li/div[2]')
        i=0
        for quote in quotes:
            item = QidianscrapyItem()
            item['Title'] = quote.xpath('child::h4/a/text()').extract_first()
            item['Author'] = quote.xpath('child::p[1]/a[1]/text()').extract_first()
            item['Url'] = 'https:'+quote.xpath('child::h4/a/@href').extract_first()
            item['FictionClass1'] = quote.xpath('child::p[1]/a[2]/text()').extract_first()
            item['FictionClass2'] = quote.xpath('child::p[1]/a[3]/text()').extract_first()
            item['State'] = quote.xpath('child::p[1]/span/text()').extract_first()
            item['Content'] = quote.xpath('child::p[2]/text()').extract_first().strip()
            item['Number'] = self.get_encode(cmap,numberlist[i][:-1])
            i+=1
            yield item
