import logging
from datetime import datetime


class ParaguayAuthMiddleware(object):

    def __init__(self, spider):
        self.spider = spider
        logging.info('Initialized authentication middleware with spider: {}.'.format(self.spider))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_request(self, request, spider):
        token = AuthManager.get_access_token(self.spider)
        request.headers['Authorization'] = token
        if self.spider.expires_soon(AuthManager.request_count, datetime.now() - AuthManager.start_time):
            AuthManager.reset_access_token(self.spider)

    def process_response(self, request, response, spider):
        if response.status == 401:
            logging.info('401 returned for request to {}'.format(request.url))
            if not AuthManager.access_token == request.headers['Authorization']:
                AuthManager.reset_access_token(self.spider)
            request.headers['Authorization'] = AuthManager.get_access_token(self.spider)
            return request
        return response


class AuthManager(object):
    access_token = None
    start_time = None
    request_count = 0

    @classmethod
    def get_access_token(cls, spider):
        if cls.access_token is None:
            cls.reset_access_token(spider)
        cls.request_count = cls.request_count + 1
        return cls.access_token

    @classmethod
    def reset_access_token(cls, spider):
        cls.start_time = datetime.now()
        cls.request_count = 0
        cls.access_token = spider.request_access_token()
