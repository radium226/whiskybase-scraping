# -*- coding: utf-8 -*-
from scrapy import Field, Spider, Item, Request
from pathlib import Path
from pprint import pprint
from itertools import islice
from scrapy.crawler import CrawlerProcess

def strip(text):
    if text:
        return text.strip()
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

class WhiskiesSpider(Spider):
    name = 'whiskies'
    allowed_domains = ['www.whiskybase.com']

    def __init__(self, search_term=None, *args, **kwargs):
        self.start_urls = [f"https://www.whiskybase.com/search?q={search_term}"]
        self.search_term = search_term
        super().__init__(**kwargs)

    def parse_price(self, response):
        whisky = response.meta["whisky"]
        whisky["average_price"] = strip(response.css(".block-shopping .block-price").xpath("p[2]/text()").get())
        whisky["lower_price"] = strip(response.css(".block-shopping .block-shoplinks").xpath("p[3]/text()").get())
        print(whisky)
        yield whisky

    def parse(self, response):
        for tr in islice(response.css("table.whiskytable tbody tr"), 2):
            url = strip(tr.xpath("td[3]/a/@href").get())
            whisky = Whisky(
                url = url,
                name = strip(tr.xpath("td[3]/a/text()").get()),
                serie = strip(tr.xpath("td[3]/span/text()").get()),
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
