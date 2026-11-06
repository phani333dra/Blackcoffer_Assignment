
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# 1. Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_DIR / "data" / "input" / "Input.xlsx"

OUTPUT_DIR = PROJECT_DIR / "data" / "output"

REPORT_FILE = OUTPUT_DIR / "url_validation_report.xlsx"

VALID_FILE = (
    PROJECT_DIR / "data" / "input" / "Input_validated.xlsx"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# 2. Validate one article URL
def validate_url(row):

    url_id = row["URL_ID"]
    url = row["URL"]

    result = {
        "URL_ID": url_id,
        "URL": url,
        "HTTP_STATUS": None,
        "TITLE": "",
        "BODY_CHARACTERS": 0,
        "VALID": False,
        "ERROR": ""
    }

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        result["HTTP_STATUS"] = response.status_code

        response.raise_for_status()

        # Check the final website domain
        final_domain = urlparse(response.url).netloc.lower()

        if final_domain not in [
            "insights.blackcoffer.com",
            "www.insights.blackcoffer.com"
        ]:
            result["ERROR"] = "Redirected outside Blackcoffer Insights"
            return result

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Find article title
        title_tag = soup.find("h1")

        if title_tag:
            result["TITLE"] = title_tag.get_text(
                " ",
                strip=True
            )

        # Remove unwanted elements
        for unwanted in soup.select(
            "script, style, nav, footer, header, aside, form"
        ):
            unwanted.decompose()

        # Find article body using common WordPress selectors
        selectors = [
            ".td-post-content",
            ".entry-content",
            ".post-content",
            "article"
        ]

        article_text = ""

        for selector in selectors:

            content = soup.select_one(selector)

            if content:
                article_text = content.get_text(
                    " ",
                    strip=True
                )

                if len(article_text) > 100:
                    break

        result["BODY_CHARACTERS"] = len(article_text)

        # A valid page must have a title and meaningful article text
        if (
            response.status_code == 200
            and result["TITLE"]
            and len(article_text) > 100
        ):
            result["VALID"] = True
        else:
            result["ERROR"] = (
                "Missing title or insufficient article text"
            )

    except requests.RequestException as error:
        result["ERROR"] = str(error)

    except Exception as error:
        result["ERROR"] = str(error)

    return result


# 3. Main program
def main():

    print("Reading Input.xlsx...")

    df = pd.read_excel(INPUT_FILE)

    print("Total URLs to validate:", len(df))

    results = []

    print("\nChecking article URLs...\n")

    # Use only 3 simultaneous requests
    with ThreadPoolExecutor(max_workers=3) as executor:

        futures = [
            executor.submit(validate_url, row)
            for _, row in df.iterrows()
        ]

        for count, future in enumerate(
            as_completed(futures),
            start=1
        ):

            results.append(future.result())

            if count % 25 == 0:
                print(
                    f"Checked {count}/{len(df)} URLs"
                )

    # 4. Create validation report
    report = pd.DataFrame(results)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    report.to_excel(
        REPORT_FILE,
        index=False
    )

    # 5. Save only validated articles separately
    valid_articles = report[
        report["VALID"] == True
    ][["URL_ID", "URL"]].sort_values("URL_ID")

    valid_articles.to_excel(
        VALID_FILE,
        index=False
    )

    # 6. Print final summary
    print("\n========== VALIDATION SUMMARY ==========")

    print("Total URLs:", len(report))

    print("Valid articles:", len(valid_articles))

    print(
        "Invalid URLs:",
        len(report) - len(valid_articles)
    )

    print("\nValidation report:", REPORT_FILE)

    print("Validated input file:", VALID_FILE)

    print("\nValidation completed!")


if __name__ == "__main__":
    main()
