# -*- coding: utf-8 -*-
from scrapy import Field, Spider, Item, Request
from pathlib import Path
from pprint import pprint
from itertools import islice
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import re
import itertools as it


def strip(text):
    if text:
        return text.strip()
    else:
        return None


def text(e):
    t = e.get()
    if t:
        return strip(BeautifulSoup(t, features="lxml").get_text())
    return None


def extract_currency(text):
    if text:
        match = re.search("^(.*?)[0-9,.]+(.*)$", text)
        if match:
            try:
                group_1 = match.group(1)
            except:
                group_1 = ""

            try:
                group_2 = match.group(2)
            except:
                group_2 = ""

            currency = (group_1 + group_2).strip()
            print(f"currency={currency}")
            currency = currency if currency != "" else None

            return currency
        return None
    return None


def extract_price(text):
    if text:
        match = re.search('([0-9,.]+)', text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        return None


def extract_details(response):
    details = dict()
    for dt, dd in zip(response.css("#whisky-details dl dt"), response.css("#whisky-details dl dd")):
        details[text(dt)] = text(dd)
    return details


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
    average_price_ccy = Field()
    lower_price = Field()
    lower_price_ccy = Field()
    bottler = Field()
    vintage = Field()
    distillery = Field()


class WhiskiesSpider(Spider):

    name = 'whiskies'
    allowed_domains = ['www.whiskybase.com']

    def __init__(self, type = None, year=None, term=None, *args, **kwargs):
        super().__init__(**kwargs)
        self.type = type
        self.new_releases_year = year
        self.search_term = term

    def start_requests(self):
        routes = {
            "new-releases": lambda spider: Request(f"https://www.whiskybase.com/whiskies/new-releases?style=table&bottle_date_year={spider.new_releases_year}", callback=self.parse_new_releases),
            "search": lambda spider: Request(f"https://www.whiskybase.com/search?q={spider.search_term}", callback=self.parse_search)
        }

        yield routes[self.type](self)



    def parse_details(self, response):
        details = extract_details(response)
        whisky = response.meta["whisky"]
        whisky["average_price"] = extract_price(strip(response.css(".block-shopping .block-price").xpath("p[2]/text()").get()))
        whisky["average_price_ccy"] = extract_currency(strip(response.css(".block-shopping .block-price").xpath("p[2]/text()").get()))
        whisky["lower_price"] = extract_price(strip(response.css("#panel-shoplinks .wb--shop-links-panel--price").xpath("text()").get()))
        whisky["lower_price_ccy"] = extract_currency(strip(response.css("#panel-shoplinks .wb--shop-links-panel--price").xpath("text()").get()))
        whisky["bottler"] = details["Bottler"]

        whisky["vintage"] = details["Vintage"] if "Vintage" in details else None
        whisky["distillery"] = details["Distillery"] if "Distillery" in details else None

        yield whisky


    def parse_whisky(self, tr, offset):
        url = strip(tr.xpath(f"td[{1 + offset}]/a/@href").get())
        whisky = Whisky(
            url = url,
            name = strip(tr.xpath(f"td[{1 + offset}]/a/text()").get()),
            serie = text(tr.xpath(f"td[{1 + offset}]/a/span")),
            stated_age = strip(tr.xpath(f"td[{2 + offset}]/text()").get()),
            strength = strip(tr.xpath(f"td[{3 + offset}]/text()").get()),
            size = strip(tr.xpath(f"td[{4 + offset}]/text()").get()),
            bottled = strip(tr.xpath(f"td[{5 + offset}]/text()").get()),
            cask_number = strip(tr.xpath(f"td[{7 + offset}]/text()").get()),
            bar_code = strip(tr.xpath(f"td[{7 + offset}]/text()").get()),
            rating = strip(tr.xpath(f"td[{8 + offset}]/text()").get())
        )
        request = Request(url, callback=self.parse_details)
        request.meta['whisky'] = whisky
        yield request

    def parse_search(self, response):
        for tr in response.css("table.whiskytable tbody tr"):
            yield from self.parse_whisky(tr, 2)

    def parse_new_releases(self, response):
        for tr in response.css("table.whiskytable tbody tr"):
            yield from self.parse_whisky(tr, 1)
