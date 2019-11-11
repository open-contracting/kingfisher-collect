import os

from kingfisher_scrapy.cli.commands.base import CLICommand
from kingfisher_scrapy.scrape_report import ScrapeReport


class ScrapeReportCLICommand(CLICommand):
    command = 'scrape-report'

    def configure_subparser(self, subparser):
        subparser.add_argument("logfilename", help="The Log File of the scrape to get stats for")

    def run_command(self, args):
        log_file_name_absolute = os.path.abspath(args.logfilename)
        scrape_report = ScrapeReport(log_file_name_absolute)
        scrape_report.go()
        scrape_report.print_output()
