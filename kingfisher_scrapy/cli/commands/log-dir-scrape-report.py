import os

from kingfisher_scrapy.cli.commands.base import CLICommand
from kingfisher_scrapy.scrape_report import LogDirScrapeReport


class LogDirScrapeReportCLICommand(CLICommand):
    command = 'log-dir-scrape-report'

    def configure_subparser(self, subparser):
        subparser.add_argument("logdirectory", help="The Log Directory to make stats files for")

    def run_command(self, args):
        log_directory_absolute = os.path.abspath(args.logdirectory)
        log_dir_scrape_report = LogDirScrapeReport(log_directory_absolute)
        log_dir_scrape_report.go()
