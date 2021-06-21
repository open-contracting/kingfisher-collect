FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# prepare deploy
RUN mkdir ~/.config
COPY docker_scrapy.cfg ~/.config/scrapy.cfg

RUN mkdir /data

ENTRYPOINT [ "bash -c 'sleep 5; scrapyd-deploy' & scrapyd" ]