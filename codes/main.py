"""
This script file presents the usage of the scrapers stored in the codes/util folder.
- scraper_aea can be used for all AEA-journals, e.g., AER, JEP, AEJMacro.
- scraper_jpe can be used for journals in associated with the Chicago Press, e.g., JPE, JOLE
- scraper_oxford can be used for journals in associated with the Oxford Press, e.g., REStud, QJE
- scraper_wiley can be used for journals in associated with the Wiley Press, e.g., ECMA, IER, QE

The key input is the issue webpage for a journal.
The outputs are markdown files storing the title, abstract, doi, pdf link, and paper link.

Author: Wang Wenzhi
Time: Tests take place in 2025-06-13.
"""

from util.scraper_aea import scrape_issue_to_markdown as scrape_aea
from util.scraper_jpe import scrape_issue_to_markdown as scrape_jpe
from util.scraper_oxford import scrape_issue_to_markdown as scrape_oxford
from util.scraper_wiley import scrape_issue_to_markdown as scrape_wiley


def main_jpe():
    issue_url = "https://www.journals.uchicago.edu/toc/jpe/2017/125/1"
    output_file = "../output/JPE_Year2017Number1.md"
    scrape_jpe(issue_url, md_path=output_file)


def main_qje():
    issue_url = "https://academic.oup.com/qje/issue/132/1"
    output_file = "../output/QJE_Year2017Number1.md"
    scrape_oxford(issue_url, md_path=output_file)


def main_aer():
    issue_url = "https://www.aeaweb.org/issues/489"
    output_file = "../output/AER_Year2017Number12.md"
    scrape_aea(issue_url, md_path=output_file)


def main_res():
    issue_url = "https://academic.oup.com/restud/issue/84/1"
    output_file = "../output/REStud_Year2017Number1.md"
    scrape_oxford(issue_url, md_path=output_file)


def main_ecma():
    issue_url = "https://onlinelibrary.wiley.com/toc/14680262/2017/85/6"
    output_file = "../output/ECMA_Year2017Number6.md"
    scrape_wiley(issue_url, md_path=output_file)


if __name__ == "__main__":
    main_jpe()
    main_qje()
    main_aer()
    main_res()
    main_ecma()
