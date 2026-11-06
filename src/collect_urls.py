
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import time

# 1. Project location
PROJECT_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    PROJECT_DIR / "data" / "input" / "Input.xlsx"
)

BASE_URL = "https://insights.blackcoffer.com"

# 2. Main article archive pages
CATEGORIES = [
    BASE_URL + "/category/our-success-stories/",
    BASE_URL + "/category/our-solutions/",
    BASE_URL + "/category/what-we-think/",
    BASE_URL + "/category/how-to/"
]

# 3. Browser-like request headers
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
session.headers.update(HEADERS)

# Store unique article URLs
article_urls = set()


# 4. Download a webpage
def get_soup(url):

    try:
        response = session.get(
            url,
            timeout=25
        )

        response.raise_for_status()

        return BeautifulSoup(
            response.text,
            "html.parser"
        )

    except requests.RequestException as error:

        print("Error accessing:", url)
        print(error)

        return None


# 5. Check whether a URL is an article
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
        "wp-admin/",
        "feed/"
    ]

    if any(
        path.lower().startswith(item)
        for item in excluded
    ):
        return False

    # Article links on this website normally
    # have a single slug in the URL path.
    if "/" in path:
        return False

    return True


# 6. Find the number of archive pages
def find_total_pages(soup):

    maximum_page = 1

    for link in soup.find_all("a", href=True):

        href = link["href"]

        match = re.search(
            r"/page/(\d+)/?$",
            urlparse(href).path
        )

        if match:
            page_number = int(match.group(1))
            maximum_page = max(
                maximum_page,
                page_number
            )

    return maximum_page


# 7. Collect article links from one archive page
def collect_articles(soup):

    found = set()

    # Article titles are displayed inside h2/h3 headings
    for link in soup.select(
        "h2 a[href], h3 a[href]"
    ):

        url = urljoin(
            BASE_URL,
            link["href"]
        )

        if is_article_url(url):

            parsed = urlparse(url)

            clean_url = (
                "https://insights.blackcoffer.com"
                + parsed.path.rstrip("/")
                + "/"
            )

            found.add(clean_url)

    return found


# 8. Main program
def main():

    print("Starting Blackcoffer URL collection...\n")

    for category in CATEGORIES:

        print("\nChecking archive:", category)

        first_page = get_soup(category)

        if first_page is None:
            continue

        total_pages = find_total_pages(first_page)

        print("Archive pages found:", total_pages)

        # Visit every page in this category
        for page_number in range(1, total_pages + 1):

            if page_number == 1:
                page_url = category
            else:
                page_url = (
                    category.rstrip("/")
                    + f"/page/{page_number}/"
                )

            print("Visiting:", page_url)

            if page_number == 1:
                soup = first_page
            else:
                soup = get_soup(page_url)

            if soup is None:
                continue

            new_links = collect_articles(soup)

            previous_count = len(article_urls)

            article_urls.update(new_links)

            added = len(article_urls) - previous_count

            print(
                "New links:", added,
                "| Total unique links:", len(article_urls)
            )

            # Be respectful to the website
            time.sleep(1)

        # Save progress after each archive
        save_to_excel()

    print("\n================================")
    print("URL COLLECTION FINISHED")
    print("Total unique URLs:", len(article_urls))
    print("================================")


# 9. Save the Excel file
def save_to_excel():

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

    print("Excel progress saved:", len(urls), "URLs")


if __name__ == "__main__":
    main()
