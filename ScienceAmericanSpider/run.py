from scrapy import cmdline

name = 'SASpider'
cmd = 'scrapy crawl {0}'.format(name)


cmdline.execute(cmd.split())
