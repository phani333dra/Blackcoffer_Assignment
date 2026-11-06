# Blackcoffer Data Extraction and Text Analysis

## 1. Project Overview

This project collects article URLs from the Blackcoffer Insights website, extracts article titles and text, and performs dictionary-based text analysis.

The project calculates the 13 text analysis variables specified in the assignment.

## 2. Project Structure

```text
submission/
│
├── src/
│   ├── collect_urls.py
│   ├── validate_urls.py
│   ├── extract_articles.py
│   └── text_analysis.py
│
├── data/
│   ├── input/
│   │   ├── Input.xlsx
│   │   └── Input_validated.xlsx
│   │
│   └── output/
│       ├── Blackcoffer_Output.xlsx
│       └── url_validation_report.xlsx
│
├── articles/
│   └── Extracted article text files (.txt)
│
├── resources/
│   ├── StopWords/
│   └── MasterDictionary/
│
├── requirements.txt
└── README.md
```

## 3. Technologies Used

- Python
- Pandas
- BeautifulSoup
- Requests
- NLTK
- OpenPyXL

## 4. Installation

Install Python 3 and open the project folder in the terminal.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the required libraries:

```powershell
python -m pip install -r requirements.txt
```

Download the required NLTK resources:

```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

## 5. Execution

Run the scripts in the following order:

**Step 1: Collect URLs**

```powershell
python src/collect_urls.py
```

**Step 2: Validate URLs**

```powershell
python src/validate_urls.py
```

**Step 3: Extract Article Text**

```powershell
python src/extract_articles.py
```

**Step 4: Perform Text Analysis**

```powershell
python src/text_analysis.py
```

## 6. Text Analysis Variables

The program calculates:

1. Positive Score
2. Negative Score
3. Polarity Score
4. Subjectivity Score
5. Average Sentence Length
6. Percentage of Complex Words
7. Fog Index
8. Average Number of Words Per Sentence
9. Complex Word Count
10. Word Count
11. Syllable Per Word
12. Personal Pronouns
13. Average Word Length

## 7. Execution Results

- Validated URLs: 1,008
- Successfully extracted and analysed articles: 1,001
- Skipped URLs: 7
- Output records: 1,001
- Output columns: 15

The following URL IDs were skipped because they did not contain usable article text:

10, 273, 554, 849, 861, 924, 940.

## 8. Output

The final analysis results are saved in:

`data/output/Blackcoffer_Output.xlsx`

The output contains the URL ID, URL, and all 13 calculated text analysis variables.