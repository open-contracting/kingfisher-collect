# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import hashlib

from scrapy.utils.python import to_bytes
from scrapy.pipelines.files import FilesPipeline


class KingfisherFilesPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None):
        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        media_ext = os.path.splitext(url)[1] 
        # Put files in a directory named after the scraper they came from
        return '%s/%s%s' % (info.spider.name, media_guid, media_ext)
