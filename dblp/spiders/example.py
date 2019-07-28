# -*- coding: utf-8 -*-
import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    custom_settings = {
        'DOWNLOAD_DELAY' : 1,
        'ROBOTSTXT_OBEY' : False,
        'DEFAULT_REQUEST_HEADERS' : {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'},
    }
    #allowed_domains = ['example.com']
    #start_urls = ['https://dblp.uni-trier.de/db/conf/icse/icse2019.html']
    def start_requests(self):
        url = getattr(self, 'seedUrl', None)
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        headers = response.xpath('//ul[@class="publ-list"]/preceding-sibling::header')[1:]
        headers = headers.xpath('h2/text()').getall()

        classes = response.xpath('//ul[@class="publ-list"]')[1:]
        classUrls = []
        for aClass in classes:
            eeUrls = aClass.xpath('.//li[@class="ee"]/a/@href').getall()
            classUrls.append(eeUrls)

        for header,urls in zip(headers,classUrls):
            for url in urls:
                yield scrapy.Request(url,callback=self.parseEe,cb_kwargs={'header' : header})

    def parseEe(self, response, header):
        url = response.xpath('//a[@name="FullTextPDF"]/@href').get()
        url = response.urljoin(url)
        title = response.xpath('//div[@id="divmain"]//h1/text()').get()
        
        #from scrapy.shell import inspect_response
        #inspect_response(response,self)
        yield {
            'header' : header,
            'title' : title,
            'url' : url,
        }
