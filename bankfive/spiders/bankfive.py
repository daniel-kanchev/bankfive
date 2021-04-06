import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankfive.items import Article


class bankfiveSpider(scrapy.Spider):
    name = 'bankfive'
    start_urls = ['https://www.bankfive.com/Resources/Learning/Blog']

    def parse(self, response):
        links = response.xpath('//a[text()="Read full article"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//ul[@class="list-inline pager"]//a/@href').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="info-wrapper"]/text()').get()
        if date:
            date = " ".join(date.split()[:3])

        content = response.xpath('//article[@class="blog-body-content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
