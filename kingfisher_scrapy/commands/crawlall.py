from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError


class CrawlAll(ScrapyCommand):
    def short_desc(self):
        return "Run all spiders"

    def syntax(self):
        return "[options] [spider ...]"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_argument("--dry-run", action="store_true", help="Runs the spiders without writing any files")
        parser.add_argument("--sample", type=int, help="The number of files to write")

    def run(self, args, opts):
        if not (bool(opts.dry_run) ^ bool(opts.sample)):
            raise UsageError("Exactly one of --dry-run or --sample must be set.")

        if opts.sample is not None and opts.sample <= 0:
            raise UsageError("--sample must be a positive integer.")

        kwargs = {}
        extensions = {"scrapy.extensions.telnet.TelnetConsole": None}

        if opts.dry_run:
            kwargs["sample"] = 1
        else:
            extensions["kingfisher_scrapy.extensions.FilesStore"] = 100

        if opts.sample:
            kwargs["sample"] = opts.sample

        # Stop after one item or error.
        self.settings.set("CLOSESPIDER_ERRORCOUNT", 1)
        # Disable LogStats extension.
        self.settings.set("LOGSTATS_INTERVAL", None)
        # Disable custom and Telnet extensions.
        self.settings.set("EXTENSIONS", extensions)

        for spider_name in self.crawler_process.spider_loader.list():
            if not args or spider_name in args:
                spidercls = self.crawler_process.spider_loader.load(spider_name)
                self.crawler_process.crawl(spidercls, **kwargs)

        self.crawler_process.start()
