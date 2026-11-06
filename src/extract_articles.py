
from pathlib import Path
import time
import re

import requests
import pandas as pd
from bs4 import BeautifulSoup


# ==================================================
# 1. PROJECT PATHS AND SETTINGS
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_DIR / "data" / "input" / "Input_validated.xlsx"
)

ARTICLES_DIR = PROJECT_DIR / "articles"

# TEST MODE:
# Process only the first 5 articles.
# Change to None after successful testing.
TEST_LIMIT = None

BASE_URL = "https://insights.blackcoffer.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
session.headers.update(HEADERS)


# ==================================================
# 2. DOWNLOAD ARTICLE WEBPAGE
# ==================================================

def download_page(url):

    try:

        response = session.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        # Convert HTML bytes into BeautifulSoup
        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        return soup

    except requests.RequestException as error:

        print("Download failed:", url)
        print("Reason:", error)

        return None


# ==================================================
# 3. EXTRACT ARTICLE TITLE AND BODY
# ==================================================




def extract_article(soup):

    # 1. Extract the article title
    title_tag = soup.find("h1")

    if title_tag:
        title = title_tag.get_text(" ", strip=True)
    else:
        title = ""

    # 2. Find the main article content
    content_selectors = [
        ".td-post-content",
        ".entry-content",
        ".post-content",
        "article .post-content",
        "article"
    ]

    content = None

    for selector in content_selectors:
        content = soup.select_one(selector)

        if content:
            break

    if content is None:
        return title, ""

    # 3. Remove unrelated HTML elements
    unwanted_selectors = [
        "script",
        "style",
        "iframe",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        ".sharedaddy",
        ".td-post-sharing",
        ".author-box",
        ".comments",
        ".related-posts"
    ]

    for selector in unwanted_selectors:
        for element in content.select(selector):
            element.decompose()

    # 4. Remove promotional sections
    promotional_headings = [
        "project snapshots",
        "summarize",
        "contact details"
    ]

    for heading in list(content.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p"]
    )):

        heading_text = heading.get_text(
            " ",
            strip=True
        ).lower().rstrip(":")

        if heading_text not in promotional_headings:
            continue

        heading_level = (
            int(heading.name[1])
            if heading.name.startswith("h")
            else None
        )

        # Store the next sibling before deleting the heading
        current = heading.find_next_sibling()

        heading.decompose()

        # Remove the promotional content until the next section
        while current is not None:

            next_element = current.find_next_sibling()

            if current.name in [
                "h1", "h2", "h3",
                "h4", "h5", "h6"
            ]:

                next_level = int(current.name[1])

                if heading_level is None or next_level <= heading_level:
                    break

            current.decompose()
            current = next_element

    # 5. Extract article text
    block_tags = [
        "h1", "h2", "h3", "h4",
        "h5", "h6",
        "p", "li", "blockquote",
        "td", "th"
    ]

    text_blocks = []

    for element in content.find_all(block_tags):

        # Avoid extracting nested text more than once
        parent = element.parent
        nested_block = False

        while parent is not None and parent != content:

            if parent.name in block_tags:
                nested_block = True
                break

            parent = parent.parent

        if nested_block:
            continue

        # Extract text and preserve spaces between HTML elements
        text = element.get_text(
            separator=" ",
            strip=True
        )

        # Normalize whitespace inside each text block
        text = re.sub(r"\s+", " ", text).strip()

        if text:
            text_blocks.append(text)

    
    # 6. Remove standalone gallery label
    if len(text_blocks) >= 2:
        if (
            text_blocks[-1].strip().lower() == "home"
            and "://" in text_blocks[-2]
        ):
            text_blocks.pop()

    # 7. Join paragraphs AFTER removing unwanted text
    article_body = "\n\n".join(text_blocks)

    # 8. Final whitespace cleanup
    article_body = re.sub(
        r"[ \t]+",
        " ",
        article_body
    )

    article_body = re.sub(
        r"\n{3,}",
        "\n\n",
        article_body
    )

    return title, article_body




# ==================================================
# 4. SAVE ARTICLE AS TXT FILE
# ==================================================

def save_article(url_id, title, body):

    file_path = ARTICLES_DIR / f"{url_id}.txt"

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(title)

        file.write("\n\n")

        file.write(body)

    return file_path


# ==================================================
# 5. PROCESS ARTICLES
# ==================================================

def main():

    print("Starting article extraction...\n")

    # Check input file
    if not INPUT_FILE.exists():

        print("Input file not found:", INPUT_FILE)
        return

    # Create articles folder
    ARTICLES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Read validated URLs
    dataframe = pd.read_excel(INPUT_FILE)
    

    # Test mode
    if TEST_LIMIT is not None:

        dataframe = dataframe.head(TEST_LIMIT)

    total_articles = len(dataframe)

    print("Articles to process:", total_articles)

    successful = 0
    failed = 0

    # Process each article
    for _, row in dataframe.iterrows():

        url_id = int(row["URL_ID"])

        url = row["URL"]

        print("\n----------------------------------")
        print("Processing URL_ID:", url_id)

        # Download webpage
        soup = download_page(url)

        if soup is None:

            failed += 1
            continue

        # Extract article information
        title, body = extract_article(soup)
        
        
        # Check extracted content
        if not title or not body.strip() or (len(body.strip()) < 100 and url_id != 836):
            print("Insufficient article content:", url_id)
            failed += 1
            continue


        # Save article
        file_path = save_article(
            url_id,
            title,
            body
        )

        successful += 1

        print("Title:", title)

        print("Body characters:", len(body))

        print("Saved:", file_path.name)

        # Wait before requesting another article
        time.sleep(1)

    # Final summary
    print("\n==================================")
    print("ARTICLE EXTRACTION COMPLETED")
    print("==================================")

    print("Total articles processed:", total_articles)

    print("Successful articles:", successful)

    print("Failed articles:", failed)

    print("Output folder:", ARTICLES_DIR)


# ==================================================
# 6. PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":

    main()
