#coding:utf-8
import json
import logging
import os
import pycurl
import re
from hashlib import sha1
from WebHub.items import PornVideoItem
from WebHub.pornhub_type import PH_TYPES
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider


class Spider(CrawlSpider):
    name = 'pornHubSpider'
    host = 'https://www.pornhub.com'
    file_dir = 'E:\\pic'
    start_urls = list(set(PH_TYPES))

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.DEBUG,
        format=
        '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='cataline.log',
        filemode='w')

    # test = True
    def start_requests(self):
        for ph_type in self.start_urls:
            yield Request(url='https://www.pornhub.com/%s' % ph_type,
                          callback=self.parse_ph_key)

    def parse_ph_key(self, response):
        selector = Selector(response)
        logging.debug('request url:------>' + response.url)
        # logging.info(selector)
        divs = selector.xpath('//div[@class="phimage"]')
        for div in divs:
            # logging.debug('divs :------>' + div.extract())

            viewkey = re.findall('viewkey=(.*?)"', div.extract())
            # logging.debug(viewkey)
            yield Request(url='https://www.pornhub.com/embed/%s' % viewkey[0],
                          callback=self.parse_ph_info)
        url_next = selector.xpath(
            '//a[@class="orangeButton" and text()="Next "]/@href').extract()
        logging.debug(url_next)
        if url_next:
            # if self.test:
            logging.debug(' next page:---------->' + self.host + url_next[0])
            yield Request(url=self.host + url_next[0],
                          callback=self.parse_ph_key)
            # self.test = False

    def parse_ph_info(self, response):
        ph_item = PornVideoItem()
        selector = Selector(response)
        # logging.info(selector)
        _ph_info = re.findall('var flashvars =(.*?),\n', selector.extract())
        logging.debug('PH信息的JSON:')
        logging.debug(_ph_info)
        _ph_info_json = json.loads(_ph_info[0])

        image_url = _ph_info_json.get('image_url')
        duration = _ph_info_json.get('video_duration')
        title = _ph_info_json.get('video_title')
        link_url = _ph_info_json.get('link_url')
        quality_480p = _ph_info_json.get('quality_480p')

        ph_item['video_duration'] = duration
        ph_item['video_title'] = title
        ph_item['image_url'] = image_url
        ph_item['link_url'] = link_url
        ph_item['quality_480p'] = quality_480p
        sha1_object = sha1()
        sha1_object.update(quality_480p)
        file_sha1 = sha1_object.hexdigest()
        # 检查这个文件有没有下载过了
        image_file_name = os.path.join(self.file_dir, file_sha1 + '.jpg')
        mp4_file_name = os.path.join(self.file_dir, file_sha1 + '.mp4')
        if os.path.exists(mp4_file_name):
            ph_item['exists'] = True
            yield ph_item
        else:
            ph_item['exists'] = False
            ph_item['video_file_path'] = mp4_file_name
            ph_item['image_file_path'] = image_file_name
            # urllib.urlretrieve(image_url, image_file_name)
            curl = pycurl.Curl()
            # curl.setopt(pycurl.USERAGENT,response.headers["User-Agent"])
            curl.setopt(pycurl.URL, image_url)
            curl.setopt(pycurl.REFERER, response.url)
            curl.setopt(pycurl.SSL_VERIFYPEER, 1)
            curl.setopt(pycurl.SSL_VERIFYHOST, 2)
            curl.setopt(pycurl.WRITEDATA, file(image_file_name, "wb"))
            curl.perform()
            curl.close()
            curl2 = pycurl.Curl()
            curl2.setopt(pycurl.URL, quality_480p)
            curl2.setopt(pycurl.REFERER, response.url)
            curl2.setopt(pycurl.SSL_VERIFYPEER, 1)
            curl2.setopt(pycurl.SSL_VERIFYHOST, 2)
            curl2.setopt(pycurl.WRITEDATA, file(mp4_file_name, "wb"))
            curl2.perform()
            curl2.close()
            # urllib.urlretrieve(quality_480p, mp4_file_name)

            yield ph_item


