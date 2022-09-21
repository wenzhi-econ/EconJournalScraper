import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os


def get_issue_articles(issue_url):
    """
    Step 1: Extract all (paper title, paper link) pairs from an AEA-journal issue page.

    Parameters:
        issue_url (str): The URL of the issue page, e.g., https://www.aeaweb.org/issues/806.

    Returns:
        dict:
            A dictionary where keys are paper tiles and values are paper links.
            An empty dictionary is returned if an error occurs.
    """
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(issue_url)
        time.sleep(3)
        html = driver.page_source
    except requests.exceptions.RequestException as e:
        print(f"[ISSUE PAGE ERROR] {e}")
        driver.quit()
        return {}
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    articles = {}

    for tag in soup.find_all("h4", class_="issue-item__title"):
        a = tag.find("a", href=True)
        if a and a.text.strip():
            title = a.text.strip()
            if title.lower() in ["front matter", "jpe turnaround times", "recent referees"]:
                continue
            link = requests.compat.urljoin(issue_url, a["href"].strip())
            articles[title] = link

    return articles


def scrape_paper_info(article_url):
    """
    Step 2: Extract detailed information for a paper from a AEA-journal.

    Parameters:
        article_url (str): The URL of the article page.

    Returns:
        dict:
            A dictionary containing the following items:
            - "title": The title of the article (str or None).
            - "abstract": The abstract of the article (str or None).
            - "doi": The DOI of the article (str or None).
            - "pdf_link": The link to download the article PDF (str or None).
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(article_url)
        time.sleep(3)
        html = driver.page_source
    except Exception as e:
        print(f"[ARTICLE ERROR] {e} — URL: {article_url}")
        driver.quit()
        return {"title": None, "abstract": None, "doi": None, "pdf_link": None}
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    def safe_extract(selector_func, default=None):
        try:
            return selector_func()
        except Exception:
            return default

    title = safe_extract(
        lambda: soup.find("h1", {"class": "citation__title"}).get_text(strip=True)
    )
    abstract = safe_extract(
        lambda: soup.find("div", class_="abstractSection abstractInFull")
        .get_text(strip=True)
        .replace("Abstract", "")
    )
    doi = safe_extract(lambda: soup.find(class_="doi__text").get_text(strip=True))
    pdf_link = safe_extract(
        lambda: requests.compat.urljoin(
            article_url, soup.find("a", {"aria-label": " PDF"}, href=True)["href"]
        )
    )

    return {"title": title, "abstract": abstract, "doi": doi, "pdf_link": pdf_link}


def scrape_issue(issue_url):
    """
    Step 3: Combine step 1 and 2 to build a DataFrame for all papers in an issue in an AEA-journal.

    Parameters:
        issue_url (str): The URL of the journal issue page.

        Returns:
            pd.DataFrame:
                A DataFrame containing the following columns:
                - "paper_title": The title of the article.
                - "paper_link": The link to the article page.
                - "abstract": The abstract of the article.
                - "doi": The DOI of the article.
                - "pdf_link": The link to download the article PDF.
    """
    article_dict = get_issue_articles(issue_url)
    print(f"Found {len(article_dict)} articles")

    records = []
    for paper_title, paper_link in article_dict.items():
        print(f"Scraping: {paper_title}")
        info = scrape_paper_info(paper_link)
        record = {
            "paper_title": info["title"] or paper_title,
            "pdf_link": info["pdf_link"],
            "doi": info["doi"],
            "abstract": info["abstract"],
            "paper_link": paper_link,
        }
        records.append(record)
        time.sleep(1)

    df = pd.DataFrame(
        records, columns=["paper_title", "paper_link", "abstract", "doi", "pdf_link"]
    )
    return df


def output_markdown(df, md_path):
    """
    Step 4. Produce a markdown output for the resulting DataFrame from step 3.

    Parameters:
        df (pd.DataFrame): The output from step 3, the scrape_issue() function.
        md_path (str): The path for saving the markdown file.
    """
    md_lines = []
    for _, row in df.iterrows():
        md_lines.append(f"# {row['paper_title']}\n")
        if row["pdf_link"]:
            md_lines.append(f"**PDF Link:** {row['pdf_link']}")
        if row["paper_link"]:
            md_lines.append(f"**Paper Link:** {row['paper_link']}")
        if row["doi"]:
            md_lines.append(f"**DOI:** {row['doi']}")
        if row["abstract"]:
            md_lines.append(f"**Abstract:**\n{row['abstract']}")
        md_lines.append("")

    if os.path.exists(md_path):
        print(
            f"\nWarning: '{os.path.basename(md_path)}' already exists. "
            "Appending new content to the end."
        )
    else:
        print(f"Creating new markdown file: '{os.path.basename(md_path)}'")

    with open(md_path, "a", encoding="utf-8") as f:
        f.write("\n\n".join(md_lines))


def scrape_issue_to_markdown(issue_url, md_path):
    """
    Step 5. Combine step 3 and 4 and create a pipeline from a issue page to a markdown file.

    Parameters:
        issue_url (str): The URL of the journal issue page.
        md_path (str): The path for saving the markdown file.
    """
    df = scrape_issue(issue_url=issue_url)
    output_markdown(df, md_path=md_path)


if __name__ == "__main__":
    latest_paper = "https://www.journals.uchicago.edu/doi/10.1086/734778"
    a = scrape_paper_info(latest_paper)
    latest_issue = "https://www.journals.uchicago.edu/toc/jpe/2025/133/6"
    b = get_issue_articles(latest_issue)
