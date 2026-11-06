
import requests
import pandas as pd
from bs4 import BeautifulSoup

INPUT_FILE = "data/input/Input_validated.xlsx"
FAILED_IDS = [10, 273, 554, 836, 849, 861, 924, 940]

dataframe = pd.read_excel(INPUT_FILE)
failed_rows = dataframe[dataframe["URL_ID"].isin(FAILED_IDS)]

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
})

for _, row in failed_rows.iterrows():
    url_id = int(row["URL_ID"])
    url = row["URL"]

    print("\n" + "=" * 75)
    print("URL_ID:", url_id)

    try:
        response = session.get(url, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")

        article = soup.find("article")

        if not article:
            print("No article element found.")
            continue

        print("\nARTICLE CONTENT BLOCKS:")

        for element in article.find_all(
            ["h1", "h2", "h3", "h4", "p", "li", "blockquote"]
        ):
            text = element.get_text(" ", strip=True)

            if text:
                print(f"[{element.name}] {text[:500]}")

        print("\nTD-POST-CONTENT DETAILS:")

        content = soup.select_one(".td-post-content")

        if content:
            print("Direct child elements:")

            for child in content.find_all(recursive=False):
                text = child.get_text(" ", strip=True)
                print(
                    "Tag:", child.name,
                    "| Class:", child.get("class"),
                    "| Text:", text[:250]
                )
        else:
            print(".td-post-content not found")

    except Exception as error:
        print("ERROR:", repr(error))

print("\nCONTENT INSPECTION COMPLETED")
