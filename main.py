from weibospider import WeiboSpider

if __name__ == '__main__':
    spider = WeiboSpider()
    for status in spider.list():
        print(status.id, status.text.replace('\n', ''))
        spider.download(status)
