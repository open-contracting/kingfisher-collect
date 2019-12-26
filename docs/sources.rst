Sources
-------

Refer to the `kingfisher-scrape GitHub repository <https://github.com/open-contracting/kingfisher-scrape/tree/master/kingfisher_scrapy/spiders>`_ for the list of spiders. Each ``.py`` file is a spider; the part before the ``.py`` extension is used as the :code:`source_id` in Kingfisher, for example: ``afghanistan_releases``.

There is a special ``test_fail`` spider that deliberately generates HTTP errors. You can use this to make sure errors are recorded properly.
