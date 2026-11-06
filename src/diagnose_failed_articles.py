
import requests
import pandas as pd
from bs4 import BeautifulSoup

INPUT_FILE = "data/input/Input_validated.xlsx"

FAILED_IDS = [10, 273, 554, 836, 849, 861, 924, 940]

dataframe = pd.read_excel(INPUT_FILE)
failed_rows = dataframe[dataframe["URL_ID"].isin(FAILED_IDS)]

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
})

selectors = [
    ".td-post-content",
    ".entry-content",
    ".post-content",
    "article .post-content",
    "article",
    "main",
    "#content",
    ".content"
]

for _, row in failed_rows.iterrows():
    url_id = int(row["URL_ID"])
    url = row["URL"]

    print("\n" + "=" * 70)
    print("URL_ID:", url_id)
    print("URL:", url)

    try:
        response = session.get(url, timeout=30)

        print("HTTP Status:", response.status_code)
        print("Final URL:", response.url)
        print("HTML Length:", len(response.content))

        soup = BeautifulSoup(response.content, "html.parser")

        print("Page Title:", soup.title.get_text(" ", strip=True)
              if soup.title else "Not found")

        print("H1:", [
            h.get_text(" ", strip=True)
            for h in soup.find_all("h1")
        ])

        print("\nContent selector results:")

        for selector in selectors:
            elements = soup.select(selector)

            if elements:
                for element in elements[:2]:
                    text = element.get_text(" ", strip=True)
                    print(
                        selector,
                        "| Characters:", len(text),
                        "| Preview:", text[:180]
                    )
            else:
                print(selector, "| Not found")

    except Exception as error:
        print("ERROR:", repr(error))

print("\nDIAGNOSTIC COMPLETED")
