Command-line interface
======================

Most subcommands of the ``scrapy`` command are defined by `Scrapy <https://docs.scrapy.org/en/latest/topics/commands.html>`__. You were already :ref:`introduced<collect-data>` to ``scrapy list`` and ``scrapy crawl``. Kingfisher Collect adds a few more:

pluck
-----

Plucks one data value per publisher. It writes a CSV file with the results, and a ``pluck_skipped.json`` file giving the reason for which some spiders were skipped.

-  ``--package-pointer=STR`` (``-p``): The JSON Pointer to the value in the package.
-  ``--release-pointer=STR`` (``-r``): The JSON Pointer to the value in the release.
-  ``--truncate=NUM`` (``-t``): Truncate the value to this number of characters.

Get each publisher's publication policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   scrapy pluck --package-pointer /publicationPolicy

This writes a ``pluck-package-publicationPolicy.csv`` file, in which the second column is the spider's name, and the first column is either:

-  The value of the ``publicationPolicy`` field in the package
-  An error message, prefixed by ``error: ``
-  The reason for which the spider was closed, prefixed by ``closed: ``

Get the latest release date
~~~~~~~~~~~~~~~~~~~~~~~~~~~

And truncate to the date component of the datetime:

.. code-block:: bash

   scrapy pluck --release-pointer /date --truncate 10

This writes a ``pluck-release-date.csv`` file.

Get the publisher's name
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   scrapy pluck --package-pointer /publisher/name

This writes a ``pluck-package-publisher-name.csv`` file.

crawlall
--------

Runs all spiders.

-  ``--dry-run``: Runs the spiders without writing any files. It stops after collecting one file or file item from each spider. This can be used to test whether any spiders are broken. Add the ``--logfile debug.log`` option to write the output to a log file for easier review.
-  ``--sample=NUM``: The number of files to write. This can be used to collect a sample from each spider.

checkall
--------

Checks that spiders are documented and well-implemented. It reports whether information is missing, out-of-order, or unexpected in the docstring, and if an expected spider argument isn't implemented.

updatedocs
----------

This command is for developers of Kingfisher Collect. When a new spider is added, or when a spider's class-level docstring is updated, the developer should run this command to update ``docs/spiders.rst``:

.. code-block:: bash

   scrapy updatedocs
