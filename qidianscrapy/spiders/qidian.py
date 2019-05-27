# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider,Request
from qidianscrapy.items import QidianscrapyItem
from pyquery import PyQuery as pq
from io import BytesIO
from fontTools.ttLib import TTFont
import requests
import re
from lxml import etree

class QidianSpider(scrapy.Spider):
    name = 'qidian'
    allowed_domains = ['www.qidian.com']
    def __init__(self):
        self.start_url = 'https://www.qidian.com/all?%27'
        self.cmap = self.get_font('https://www.qidian.com/all?chanId=21&orderId=&page=1&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0')
        self.urls = self.getUrl(self.start_url)

    def get_font(self,Pageurl):
        response = requests.get(Pageurl).text
        doc = pq(response)
        # 获取当前字体文件名称
        fonturl = doc('p.update > span > style').text()
        url = re.search('woff.*?url.*?\'(.+?)\'.*?truetype', fonturl).group(1)
        response = requests.get(url)
        font = TTFont(BytesIO(response.content))
        cmap = font.getBestCmap()
        font.close()
        return cmap

    def getUrl(self,start_url):
        urlList = []
        response = etree.HTML(requests.get(start_url).text)
        # choose mian classify
        first_item = response.xpath('/html/body/div[1]/div[5]/div[1]/div[3]/div[1]/ul//li/a/@href')
        # average 4 select 1
        for url in first_item[1::4]:
            targetUrl = 'https:' + url
            val = etree.HTML(requests.get(targetUrl).text)
            urlList.extend(val.xpath('/html/body/div[1]/div[5]/div[1]/div[3]/div[1]/div/dl//@href'))
        return urlList

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
        for url in self.urls:
            url = 'https:'+url
            # page number
            for i in range(1,5):
                url = url.replace(str(i),str(i+1))
                yield Request(url,self.parse)

    def parse(self, response):
        doc = pq(response.text)
        # 获取当前字体文件名称
        classattr = doc('p.update > span > span').attr('class')
        pattern = '</style><span.*?%s.*?>(.*?)</span>' % classattr
        # 获取当前页面所有被字数字符
        numberlist = re.findall(pattern, response.text)
        try:
            quotes = response.xpath('/html/body/div[1]/div[5]/div[2]/div[2]/div/ul/li/div[2]')
        except:
            print('Xpath 1 change, please check')
        i=0
        for quote in quotes:
            item = QidianscrapyItem()
            item['Title'] = quote.xpath('h4/a/text()').extract_first()
            item['Author'] = quote.xpath('p[1]/a[1]/text()').extract_first()
            item['Url'] = 'https:'+quote.xpath('h4/a/@href').extract_first()
            item['FictionClass1'] = quote.xpath('p[1]/a[2]/text()').extract_first()
            item['FictionClass2'] = quote.xpath('p[1]/a[3]/text()').extract_first()
            item['State'] = quote.xpath('p[1]/span/text()').extract_first()
            item['Content'] = quote.xpath('p[2]/text()').extract_first().strip()
            try:
                item['Number'] = self.get_encode(self.cmap,numberlist[i][:-1])
            except KeyError:
                self.cmap = self.get_font(response.url)
                item['Number'] = self.get_encode(self.cmap, numberlist[i][:-1])
            i+=1
            yield item
