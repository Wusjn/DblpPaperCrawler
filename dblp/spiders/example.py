# -*- coding: utf-8 -*-
import scrapy
import sys


class ExampleSpider(scrapy.Spider):
    name = 'example'
    custom_settings = {
        'DOWNLOAD_DELAY' : 1,
        'ROBOTSTXT_OBEY' : False,
        'DEFAULT_REQUEST_HEADERS' : {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Accept' : '*/*',
            'Accept-Encoding' : 'identity',
        }
    }
    #allowed_domains = ['example.com']
    #start_urls = ['https://dblp.uni-trier.de/db/conf/icse/icse2019.html']
    def start_requests(self):
        url = getattr(self, 'seedUrl', None)
        yield scrapy.Request(url, self.parse)

    def https2http(self,url):
        if url.startswith('https'):
            return url[:4] + url[5:]
        else:
            return url
    
    def http2https(self,url):
        return url[:4] + 's' + url[4:]

    def selectProperUrl(self,urls):
        httpUrls = []
        for url in urls:
            httpUrls.append(self.http2https(self.https2http(url)))

        for url in httpUrls:
            if url.startswith('https://dl.acm.org'):
                return ('acm',url)
        for url in httpUrls:
            if url.startswith('https://ieeexplore.ieee.org'):
                return ('ieee',url)
        for url in httpUrls:
            if url.startswith('https://link.springer.com'):
                return ('springer',url)
        for url in httpUrls:
            if url.startswith('https://doi.org'):
                return ('doi',url)
        print("Didn't find supported url in urls below :")
        print(httpUrls)
        sys.exit(1)


    def parse(self, response):
        headers = response.xpath('//ul[@class="publ-list"]/preceding-sibling::header')[1:]
        headers = headers.xpath('h2/text()').getall()

        classes = response.xpath('//ul[@class="publ-list"]')[1:]
        classesUrls = []
        for aClass in classes:
            papers = aClass.xpath('.//li[@class="entry inproceedings"]')
            classUrls = []
            for paper in papers:
                title = paper.xpath('.//span[@class="title"]/text()').get()
                urls = paper.xpath('.//li[@class="ee"]/a/@href').getall()
                urlType,selectedUrl = self.selectProperUrl(urls)
                classUrls.append((title,urlType,selectedUrl))
            classesUrls.append(classUrls)

            
        for header,urls in zip(headers,classesUrls):
            for (title,urlType,url) in urls:
                if urlType == 'acm':
                    yield scrapy.Request(url,callback=self.parseAcm,cb_kwargs={'header' : header,'title' : title})
                elif urlType == 'ieee':
                    yield scrapy.Request(url,callback=self.parseIeee,cb_kwargs={'header' : header,'title' : title})
                elif urlType == 'springer':
                    yield scrapy.Request(url,callback=self.parseSpringer,cb_kwargs={'header' : header,'title' : title})
                elif urlType == 'doi':
                    yield scrapy.Request(url,callback=self.parseDoi,cb_kwargs={'header' : header,'title' : title})
                else:
                    print('Unknown url type : ' + urlType)
                    sys.exit(2)

    def parseAcm(self, response, header, title):
        url = response.xpath('//a[@name="FullTextPDF"]/@href').get()
        url = response.urljoin(url)
        #title = response.xpath('//div[@id="divmain"]//h1/text()').get()
        
        #from scrapy.shell import inspect_response
        #inspect_response(response,self)
        yield {
            'header' : header,
            'title' : title,
            'url' : url,
        }

    def parseIeee(self, response, header, title):
        baseUrl = 'https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='
        documentId = response.url.split('/')[-1]
        url = baseUrl + documentId

        yield {
            'header' : header,
            'title' : title,
            'url' : url,
        }

    def parseSpringer(self, response, header, title):
        url = response.xpath('.//a[@data-track-action="Pdf download"]/@href').get()
        url = response.urljoin(url)

        yield {
            'header' : header,
            'title' : title,
            'url' : url,
        }

    def parseDoi(self, response, header, title):
        url = self.https2http(response.url)
        result = None
        if url.startswith('http://dl.acm.org'):
            result = self.parseAcm(response, header, title)
        elif url.startswith('http://ieeexplore.ieee.org'):
            result = self.parseIeee(response, header, title)
        elif url.startswith('http://link.springer.com'):
            result = self.parseSpringer(response, header, title)
        else:
            print('Unknown url type : ' + url)
            sys.exit(3)
        for item in result:
            yield item

