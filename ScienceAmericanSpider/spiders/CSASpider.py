import logging
import os

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.spiders import Spider

from ScienceAmericanSpider.items import ScienceamericanspiderItem


class CSASpider(Spider):
    name = 'SASpider'
    start_urls = [
        'https://www.scientificamerican.com/mind/'
        , 'https://www.scientificamerican.com/health/'
        , 'https://www.scientificamerican.com/tech/'
        , 'https://www.scientificamerican.com/sustainability/'
        , 'https://www.scientificamerican.com/education/'
        # , 'https://www.scientificamerican.com/podcast/60-second-science/'
    ]
    custom_settings = {
        # 'DBPATH': 'C:/Users/whatseven/source/repos/ScienceAmericanSpider/db.db3',
        'DBPATH': os.path.join(os.path.abspath('..') ,'db.db3') ,
    }

    def __init__(self, *args, **kwargs):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        super().__init__(*args, **kwargs)

    # cope with subIndex
    def parse(self, response):
        # If it is a podcast
        if '60-second-science' in response.url:
            subHeaders=response.xpath("//div[contains(@data-podcast-type,'gridded-podcast')]")
            for subHeader in subHeaders:
                yield Request(subHeader.xpath("./section/div[3]/h3/a/@href").extract()[0], callback=self.parsePodCast)
            next_url = response.xpath('//footer/div[3]/a/@href').extract()
            if next_url:
                if int(next_url[0][6:])>20:
                    return
                self.logger.info("PodCast:"+next_url[0][6:])
                if 'page' in response.url:
                    next_url = response.url.split('?')[0] + next_url[0]
                else:
                    next_url = response.url + next_url[0]
                yield Request(next_url)

        # If it is an article
        else:
            subHeaders=response.xpath('//ul[contains(@class,"header-topic-list")]/li')
            for subHeader in subHeaders:
                yield Request(subHeader.xpath("./a/@href").extract()[0], callback=self.parseTitles)

    def parseTitles(self,response):
        titles = response.xpath('//h2[@class="t_listing-title"]/a')
        for title in titles:
            yield Request(title.xpath(".//@href").extract()[0], callback=self.parseItem)

        next_url = response.xpath('//footer/div[3]/a/@href').extract()
        if next_url:
            if int(next_url[0][6:])>100:
                return
            self.logger.info("Article:"+next_url[0][6:])
            if 'page' in response.url:
                next_url = response.url.split('?')[0] + next_url[0]
            else:
                next_url = response.url + next_url[0]
            yield Request(next_url,self.parseTitles)

    def parseItem(self, response):
        item = ScienceamericanspiderItem()

        if 'podcast' in response.url:
            return
            # len(response.xpath("//div[contains(@class,'player-controls')]")) != 0:
            item['isPodCast'] = True
            item['podcast'] = response.xpath('//a[contains(@class,"podcast-download")]'
                                             '/span[1][contains(@class,"icon__download--black")]/../@href').extract()[0]
            try:
                item['name'] = response.xpath("//h1[contains(@class,'article-header__title')]/text()").extract()[0]
            except:
                print(1)
            item['url'] = response.url
            item['description'] = response.xpath("string(//section[contains(@class,'article-grid__main')]"
                                                 "/div/p[1])").extract()[0]
            contents = ''
            for singleSelect in response.xpath("//section[contains(@class,'article-grid__main')]"
                                               "/div[contains(@class,'transcript')]/div[2]/p"):
                content = singleSelect.xpath("string(.)").extract()[0]
                contents += content + '\n'
            item['text'] = contents
            yield item

        elif len(response.xpath("//em[contains(.,'Continue')]")) != 0 \
                or len(response.xpath("//div[contains(@class,'paywall__header')]")) != 0:
            return

        elif 'article' in response.url:
            try:
                item['category']=response.xpath('//div[contains(@class,"article-header__inner__category")]/a/text()').extract()[0]
            except:
                print(1)
            item['fileType'] = 'article'
            try:
                item['name'] = response.xpath("//h1[contains(@class,'article-header__title')]/text()").extract()[0]
            except:
                print(1)
            item['url'] = response.url
            t=response.xpath("//p[@class='t_article-subtitle']/text()").extract()
            item['description'] = t[0] if len(t)>0 else ''
            contents = ''
            for singleSelect in response.xpath("//div[contains(@class,'article-text')]/div/div/p"):
                content = singleSelect.xpath("string(.)").extract()[0]
                contents += content + '\n'
            item['text'] = contents
            yield item
        else:
            return

    def parsePodCast(self,response):
        item = ScienceamericanspiderItem()

        if 'podcast' in response.url:
            try:
                item['category']=response.xpath('//div[contains(@class,"article-header__inner__category")]/text()').extract()[0]
            except:
                print(1)
            item['fileType'] = 'podcast'
            try:
                item['name'] = response.xpath("//h3[contains(@class,'podcasts-header__title')]/text()").extract()[0]
            except:
                print(1)
            item['url'] = response.url
            t=response.xpath("string(//section[@class='article-grid__main']/div/p)").extract()
            if len(t)>0:
                item['description'] = t[0] if len(t)>0 else ''
            else:
                t=response.xpath("string(//section[@class='article-grid__main']/div)").extract()
                item['description'] = t[0] if len(t)>0 else ''
            contents = ''
            for singleSelect in response.xpath("//section[@class='article-grid__main']/div[2]/div[2]/p"):
                content = singleSelect.xpath("string(.)").extract()[0]
                contents += content + '\n'
            item['text'] = contents
            item['podcast']=response.xpath("//a[contains(@class,'podcast-download')]/@href").extract()[0]
            yield item
        else:
            return