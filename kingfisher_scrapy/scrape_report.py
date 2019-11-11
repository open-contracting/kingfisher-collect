import os


class ScrapeReport:

    def __init__(self, log_dir_scrape_report):
        self.log_dir_scrape_report = log_dir_scrape_report
        self.stats = None

    def go(self):
        stats_text = ''
        in_stats_text = False
        with open(self.log_dir_scrape_report) as fp:
            line = fp.readline()
            while line:
                line_stripped = line.strip()
                if line_stripped.endswith('[scrapy.statscollectors] INFO: Dumping Scrapy stats:'):
                    in_stats_text = True
                elif in_stats_text:
                    stats_text += line
                    if line_stripped.endswith('}'):
                        in_stats_text = False
                line = fp.readline()
        self.stats = stats_text

    def print_output(self):
        print(self.stats)


class LogDirScrapeReport:

    def __init__(self, log_dir_scrape_report):
        self.log_dir_scrape_report = log_dir_scrape_report

    def go(self):
        for (dirpath, dirnames, filenames) in os.walk(self.log_dir_scrape_report):
            for filename in filenames:
                absolute_file_path = os.path.join(dirpath, filename)
                if absolute_file_path.endswith('.log') and not absolute_file_path.endswith('_report.log'):
                    absolute_file_path_out = absolute_file_path[:-4] + '_report.log'
                    if not os.path.exists(absolute_file_path_out):
                        scrape_report = ScrapeReport(absolute_file_path)
                        scrape_report.go()
                        # We might have found a log file that is still in the process of being written;
                        # If we can't extract stats assume that's the case and don't make a report file yet.
                        # (Otherwise it will write an empty file, but that will still stop a better report file
                        #   from being written later when the scraper is finished)
                        if scrape_report.stats:
                            with open(absolute_file_path_out, 'w') as fp:
                                fp.write(scrape_report.stats)
