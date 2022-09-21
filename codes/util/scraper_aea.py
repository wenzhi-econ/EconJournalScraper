import requests
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
    headers = {"User-Agent": "Mozilla/5.0 (compatible; scraper-bot/1.0)"}

    try:
        resp = requests.get(issue_url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ISSUE PAGE ERROR] {e}")
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = {}

    for tag in soup.find_all("article", class_=lambda c: c and c.startswith("journal-article")):
        a = tag.find("a", href=True)
        if a and a.text.strip():
            title = a.text.strip()
            if title.lower() == "front matter":
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
    headers = {"User-Agent": "Mozilla/5.0 (compatible; scraper-bot/1.0)"}

    try:
        resp = requests.get(article_url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ARTICLE ERROR] {e} — URL: {article_url}")
        return {"title": None, "abstract": None, "doi": None, "pdf_link": None}

    soup = BeautifulSoup(resp.text, "html.parser")

    def safe_extract(selector_func, default=None):
        try:
            return selector_func()
        except Exception:
            return default

    title = safe_extract(lambda: soup.find("h1").get_text(strip=True))
    abstract = safe_extract(
        lambda: soup.find("section", class_="article-information abstract")
        .get_text(strip=True)
        .replace("Abstract", "")
    )
    doi = safe_extract(
        lambda: soup.find(class_="doi").get_text(strip=True).replace("DOI:", "").strip()
    )
    pdf_link = safe_extract(
        lambda: requests.compat.urljoin(
            article_url, soup.find("a", class_="button", href=True)["href"]
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
