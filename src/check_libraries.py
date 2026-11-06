
from pathlib import Path
from urllib.parse import urlparse, urljoin
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

# 1. Project folder and Excel output location
PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_DIR / "data" / "input" / "Input.xlsx"

BASE_URL = "https://insights.blackcoffer.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# 2. Store collected article URLs without duplicates
article_urls = set()

# 3. Download a webpage
def get_soup(url):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        return BeautifulSoup(response.text, "html.parser")

    except requests.RequestException as error:
        print("Could not access:", url)
        print("Reason:", error)
        return None


# 4. Check whether a link belongs to Blackcoffer Insights
def is_article_url(url):
    parsed = urlparse(url)

    if parsed.netloc.lower() not in [
        "insights.blackcoffer.com",
        "www.insights.blackcoffer.com"
    ]:
        return False

    path = parsed.path.strip("/")

    if not path:
        return False

    excluded = [
        "category/",
        "tag/",
        "author/",
        "page/",
        "wp-content/",
        "wp-admin/"
    ]

    if any(item in parsed.path.lower() for item in excluded):
        return False

    return True


# 5. Collect article links from a webpage
def collect_from_page(page_url):
    print("Visiting:", page_url)

    soup = get_soup(page_url)

    if soup is None:
        return []

    found_links = []

    for link in soup.find_all("a", href=True):
        full_url = urljoin(BASE_URL, link["href"])

        if is_article_url(full_url):
            clean_url = full_url.split("#")[0].split("?")[0].rstrip("/") + "/"
            found_links.append(clean_url)

    return found_links


# 6. Main collection process
def main():

    # Start with the website homepage
    pages_to_visit = [
        BASE_URL
    ]

    visited_pages = set()

    while pages_to_visit and len(article_urls) < 600:

        current_page = pages_to_visit.pop(0)

        if current_page in visited_pages:
            continue

        visited_pages.add(current_page)

        links = collect_from_page(current_page)

        for link in links:
            article_urls.add(link)

        print("Unique links collected:", len(article_urls))

        # Discover pagination links
        soup = get_soup(current_page)

        if soup:
            for link in soup.find_all("a", href=True):
                next_url = urljoin(BASE_URL, link["href"])

                if (
                    BASE_URL in next_url
                    and (
                        "/page/" in next_url
                        or "paged=" in next_url
                    )
                    and next_url not in visited_pages
                ):
                    pages_to_visit.append(next_url)

        time.sleep(1)

    # 7. Save URLs in Excel
    urls = sorted(article_urls)

    dataframe = pd.DataFrame({
        "URL_ID": range(1, len(urls) + 1),
        "URL": urls
    })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataframe.to_excel(
        OUTPUT_FILE,
        index=False
    )

    print("\nCollection completed.")
    print("Total unique URLs:", len(urls))
    print("Excel saved at:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
