# -*- coding: utf-8 -*-
from scrapy import Field, Spider, Item, Request
from pathlib import Path
from pprint import pprint
from itertools import islice
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import re

def strip(text):
    if text:
        return text.strip()
    else:
        return None

def text(e):
    return strip(BeautifulSoup(e.get()).get_text())

def extract_price(text):
    if text:
        match = re.search('([0-9,.]+)', text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        return None


class Whisky(Item):

    name = Field()
    url = Field()
    serie = Field()
    stated_age = Field()
    strength = Field()
    size = Field()
    bottled = Field()
    cask_number = Field()
    bar_code = Field()
    rating = Field()
    average_price = Field()
    lower_price = Field()
    bottler = Field()

class WhiskiesSpider(Spider):
    name = 'whiskies'
    allowed_domains = ['www.whiskybase.com']

    def __init__(self, search_term=None, *args, **kwargs):
        self.start_urls = [f"https://www.whiskybase.com/search?q={search_term}"]
        self.search_term = search_term
        super().__init__(**kwargs)

    def parse_price(self, response):
        whisky = response.meta["whisky"]
        whisky["average_price"] = extract_price(strip(response.css(".block-shopping .block-price").xpath("p[2]/text()").get()))
        whisky["lower_price"] = extract_price(strip(response.css("#panel-shoplinks .wb--shop-links-panel--price").xpath("text()").get()))
        bottler = text(response.css(".block-desc dl").xpath("dd[3]"))
        whisky["bottler"] = bottler
        yield whisky

    def parse(self, response):
        for tr in islice(response.css("table.whiskytable tbody tr"), 20):
            url = strip(tr.xpath("td[3]/a/@href").get())
            whisky = Whisky(
                url = url,
                name = strip(tr.xpath("td[3]/a/text()").get()),
                serie = text(tr.xpath("td[3]/a/span")),
                stated_age = strip(tr.xpath("td[4]/text()").get()),
                strength = strip(tr.xpath("td[5]/text()").get()),
                size = strip(tr.xpath("td[6]/text()").get()),
                bottled = strip(tr.xpath("td[7]/text()").get()),
                cask_number = strip(tr.xpath("td[8]/text()").get()),
                bar_code = strip(tr.xpath("td[9]/text()").get()),
                rating = strip(tr.xpath("td[10]/text()").get())
            )
            request = Request(url, callback=self.parse_price)
            request.meta['whisky'] = whisky
            yield request
