from util.scraper_aea import scrape_issue_to_markdown as scrape_aea
from util.scraper_jpe import scrape_issue_to_markdown as scrape_jpe


def main_aer():
    issue_url = "https://www.aeaweb.org/issues/489"
    output_file = "../output/AER_Year2017Number12.md"
    scrape_aea(issue_url, md_path=output_file)


def main_jpe():
    issue_url = "https://www.journals.uchicago.edu/toc/jpe/2017/125/6"
    output_file = "../output/JPE_Year2017Number6.md"
    scrape_jpe(issue_url, md_path=output_file)


if __name__ == "__main__":
    main_aer()
    main_jpe()
