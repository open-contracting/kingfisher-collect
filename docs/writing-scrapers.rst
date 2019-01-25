Writing OCDS Kingfisher scrapers with Scrapy
--------------------------------------------

About Scrapy
~~~~~~~~~~~~

Scrapy calls scrapers 'spiders' so we're going to call them 'spiders' hereon. 

Scrapy provides a `Spider` class which all spiders should inherit, and the process of writing a new spider basically involves defining the `parse` method and overriding any of the other `Spider` methods if you need to customise what they do.

The Scrapy framework determines what happens to a crawled item through its 'pipeline', and lots of things happen in the background (like the actual sending of requests, and automatic passing things through different stages in the pipeline).

Scrapy schedules HTTP requests with its own crawler engine, and they are not guaranteed (or likely) to be executed in a predictable order.

`Scrapy documentation <https://docs.scrapy.org/en/latest/>`_.

About OCDS Kingfisher
~~~~~~~~~~~~~~~~~~~~~

The OCDS data sources are for the most part JSON APIs which output valid OCDS data, either as ``release_package``, ``record_package``, ``release``, ``record`` and a few other types, using various different structures or endpoints of the publishers' own design.

Our spiders need to:

* Know the URL(s) for a particular API from which all data can be found.
* Tell the difference between endpoints which return lists of URLS
   * And then follow these URLS
* and endpoints which return OCDS data
   * And then download this data.
* and endpoints which return both useful OCDS data and more URLs to fetch
* and endpoints which return other things.

This tends to involve prior knowledge of the API you're writing a spider for (you have to go look at its responses yourself to see what they are), and maybe some JSON parsing of the responses.

For Kingfisher, we have defined additional custom 'pipeline' components which are used by all spiders automatically, in the sequence defined in ``settings.py``. (For writing spiders you shouldn't need to worry about these.)

Using the pipeline
------------------

The custom OCDS Kingfisher scraper pipeline looks like this:

1. Each spider first finds its starting point(s). Either:
    * ``start_urls`` list or
    * requests yielded from the ``start_requests`` method.

Then, for *each* URL:

2. GET requests are passes it to the crawler engine to be executed. The response is passed back to the ``parse`` method in the spider.
3. Carries out ``parse`` on the response, which will be different for each crawler. ``parse`` must yield a dict containing the URL of a JSON file from the API being scraped, and the type of OCDS data therein.
4. The output of ``parse`` is automatically passed to the ``KingfisherFilesPipeline``, which schedules downloading of the JSON files to disc.
5. The path of the downloaded file, and relevant metadata, is passed automatically to the ``KingfisherPostPipeline`` which fires it all off to the Kingfisher Process API.

The only parts you should have to touch when writing a spider are **1** and **3**.

Spider properties
~~~~~~~~~~~~~~~~~

* ``name``: a slug for the spider. This is what you pass to ``scrapy crawl`` to run it. Underscore separated, all lowercase. Required.
* ``start_urls``: list of URLs to do the initial GET on. Don't need it if you define ``start_requests`` instead.
* See `Scrapy Spider <https://docs.scrapy.org/en/latest/topics/spiders.html#scrapy-spider>`_ docs for other options.

.. code-block:: python

    from scrapy import Spider

    class CanadaBuyAndSell(Spider):
        name = "canada_buyandsell"
        ...


Start Requests
~~~~~~~~~~~~~~

Implement the ``start_requests`` method *instead of* using a ``start_urls`` property on the spider if you need to do something more complicated than just a list to get the URLs the spider starts with.

This might be useful to generate a long list of API endpoint URLs you know are sequential or contain dates or something.

However you come up with them, the output of this method should yield a Scrapy ``Request`` for each URL.

Eg.

.. code-block:: python

    def start_requests(self):
        url_base = 'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-{}-{}.json'
        urls = []
        for year in range(13, 17):
            urls.append(url_base.format(year, year+1))

        for url in urls:
            yield scrapy.Request(url)


This does the same thing as:

.. code-block:: python

    start_urls = [
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
            'https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
        ]


Only with ``start_requests`` if we want to add a year we just up the range, or if the API endpoint changes we only need to modify one string.

Parse
~~~~~

This is where you find the URLs of API endpoints which give you one or more items of OCDS data and hand them one by one to the files downloader.

The files downloader expects a dict containing the ``files_urls`` key, which should have a list as its value. Almost certainly there will only ever be one item in your list. If you find yourself with an API response that is already a list of URLs, loop through and send them one by one - because of how Scrapy handles file downloads, it's faster.

You also need to include the ``data_type`` which corresponds to the contents of the API response.

Here's a very simple ``parse`` which just regurgitates the original request URL. Most likely you'll need to do a little JSON parsing here to get the values.

.. code-block:: python

    def parse(self, response):
        yield {
            "file_urls": [response.url], 
            "data_type": "release_package"
        }


Sample mode
~~~~~~~~~~~

Sample mode is a way to get a subset of the results, then stop the spider. It's triggered when you pass ``-a sample=true`` to ``scrapy crawl <spider_name>``. 

How sample mode is executed is different for every spider, depending on the API you're crawling. You *probably* want to define it in `start_requests` though, unless your ``start_urls`` is only one (like an index listing) in which case you'd define it in ``parse`` (where you loop through the listing).

It just needs to do something like yield a single Request for one URL in a list of URLs, instead of yielding Requests for all of the URLs in the list.

Eg. in ``start_requests``:

.. code-block:: python

    if hasattr(self, 'sample') and self.sample == 'true':
            yield scrapy.Request(urls[0])
        else:
            for url in urls:
                yield scrapy.Request(url)


Eg. in ``parse``:

.. code-block:: python

    files_urls = json.loads(response.body)
        if hasattr(self, 'sample') and self.sample == 'true':
            files_urls = [files_urls[0]]
            
        for file_url in files_urls:
            yield {
                'file_urls': [file_url],
                'data_type': 'record'
            }
