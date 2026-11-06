
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_DIR / "data" / "input" / "Input_validated.xlsx"

df = pd.read_excel(INPUT_FILE)
row = df[df["URL_ID"] == 1].iloc[0]

response = requests.get(
    row["URL"],
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.content, "html.parser")

content = soup.select_one(".td-post-content")

if content is None:
    print("Article content not found.")
    raise SystemExit

text = content.get_text(" ", strip=True)

for keyword in ["application", "resulted", "handling", "employ"]:

    print("\nSEARCH:", keyword)

    position = text.lower().find(keyword.lower())

    if position != -1:
        print(repr(text[position:position + 120]))
    else:
        print("Not found")
