
from pathlib import Path
import re

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


# ==================================================
# 1. PROJECT PATHS AND SETTINGS
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_DIR / "data" / "input" / "Input_validated.xlsx"

ARTICLES_DIR = PROJECT_DIR / "articles"

STOPWORDS_DIR = PROJECT_DIR / "resources" / "StopWords"

MASTER_DIR = PROJECT_DIR / "resources" / "MasterDictionary"

OUTPUT_TEMPLATE = (
    PROJECT_DIR / "data" / "output" / "Output Data Structure.xlsx"
)

OUTPUT_FILE = (
    PROJECT_DIR / "data" / "output" / "Blackcoffer_Output.xlsx"
)

# Initially process only 5 articles for testing.
# Change to None after successful testing.
TEST_LIMIT = None


# ==================================================
# 2. LOAD STOPWORDS AND MASTER DICTIONARY
# ==================================================


def load_custom_stopwords():

    stopword_set = set()

    for file_path in STOPWORDS_DIR.glob("*.txt"):

        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        for line in content.splitlines():

            # Read every entry separated by |
            entries = line.split("|")

            for entry in entries:

                words = re.findall(
                    r"[a-z]+",
                    entry.lower()
                )

                stopword_set.update(words)

    return stopword_set




def load_master_dictionary(file_path):
    content = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    words = set()

    for line in content.splitlines():
        word = line.strip().lower()

        # Accept only complete alphabetic words
        if re.fullmatch(r"[a-z]+", word):
            words.add(word)

    return words



# ==================================================
# 3. SYLLABLE COUNT FUNCTION
# ==================================================

def count_syllables(word):

    word = word.lower()

    # Count vowel occurrences
    syllables = sum(
        1 for character in word
        if character in "aeiou"
    )

    # Handle the specified endings
    if word.endswith(("es", "ed")) and syllables > 1:
        syllables -= 1

    # Every word should have at least one syllable
    return max(syllables, 1)


# ==================================================
# 4. PERSONAL PRONOUN COUNT
# ==================================================

def count_personal_pronouns(text):

    pronoun_pattern = (
        r"\b(?:I|we|my|ours|us)\b"
    )

    pronouns = re.findall(
        pronoun_pattern,
        text,
        flags=re.IGNORECASE
    )

    # Exclude uppercase US when it refers to the country
    country_us = re.findall(r"\bUS\b", text)

    return max(len(pronouns) - len(country_us), 0)


# ==================================================
# 5. CALCULATE TEXT ANALYSIS VARIABLES
# ==================================================

def calculate_metrics(
    text,
    custom_stopwords,
    positive_dictionary,
    negative_dictionary,
    nltk_stopwords
):

    # Tokenize the article
    tokens = word_tokenize(text)

    # Remove punctuation and keep alphabetic words
    all_words = [
        token.lower()
        for token in tokens
        if re.fullmatch(r"[A-Za-z]+", token)
    ]

    # ----------------------------------------------
    # SENTIMENT ANALYSIS
    # ----------------------------------------------

    # Remove supplied custom stopwords
    sentiment_words = [
        word for word in all_words
        if word not in custom_stopwords
    ]

    positive_score = sum(
        1 for word in sentiment_words
        if word in positive_dictionary
    )

    negative_score = sum(
        1 for word in sentiment_words
        if word in negative_dictionary
    )

    polarity_score = (
        (positive_score - negative_score)
        / (positive_score + negative_score + 0.000001)
    )

    subjectivity_score = (
        (positive_score + negative_score)
        / (len(sentiment_words) + 0.000001)
    )

    # ----------------------------------------------
    # WORD COUNT
    # ----------------------------------------------

    # Remove NLTK English stopwords
    cleaned_words = [
        word for word in all_words
        if word not in nltk_stopwords
    ]

    word_count = len(cleaned_words)

    # ----------------------------------------------
    # SENTENCE ANALYSIS
    # ----------------------------------------------

    sentences = sent_tokenize(text)

    sentence_count = len(sentences)

    if sentence_count > 0:
        average_sentence_length = (
            word_count / sentence_count
        )
    else:
        average_sentence_length = 0

    average_words_per_sentence = average_sentence_length

    # ----------------------------------------------
    # COMPLEX WORD ANALYSIS
    # ----------------------------------------------

    syllable_counts = [
        count_syllables(word)
        for word in cleaned_words
    ]

    complex_word_count = sum(
        1 for count in syllable_counts
        if count > 2
    )

    if word_count > 0:

        percentage_complex_words = (
            complex_word_count / word_count
        )

        average_syllables_per_word = (
            sum(syllable_counts) / word_count
        )

        average_word_length = (
            sum(len(word) for word in cleaned_words)
            / word_count
        )

    else:

        percentage_complex_words = 0
        average_syllables_per_word = 0
        average_word_length = 0

    # ----------------------------------------------
    # FOG INDEX
    # ----------------------------------------------

    fog_index = 0.4 * (
        average_sentence_length
        + percentage_complex_words
    )

    # ----------------------------------------------
    # PERSONAL PRONOUNS
    # ----------------------------------------------

    personal_pronouns = count_personal_pronouns(text)

    # ----------------------------------------------
    # RETURN ALL 13 VARIABLES
    # ----------------------------------------------

    return {
        "POSITIVE SCORE": positive_score,
        "NEGATIVE SCORE": negative_score,
        "POLARITY SCORE": polarity_score,
        "SUBJECTIVITY SCORE": subjectivity_score,
        "AVG SENTENCE LENGTH": average_sentence_length,
        "PERCENTAGE OF COMPLEX WORDS": percentage_complex_words,
        "FOG INDEX": fog_index,
        "AVG NUMBER OF WORDS PER SENTENCE": average_words_per_sentence,
        "COMPLEX WORD COUNT": complex_word_count,
        "WORD COUNT": word_count,
        "SYLLABLE PER WORD": average_syllables_per_word,
        "PERSONAL PRONOUNS": personal_pronouns,
        "AVG WORD LENGTH": average_word_length
    }


# ==================================================
# 6. MAIN PROGRAM
# ==================================================

def main():

    print("Starting text analysis...\n")

    # Load supplied custom stopwords
    custom_stopwords = load_custom_stopwords()

    # Load NLTK stopwords
    nltk_stopwords = set(stopwords.words("english"))

    # Load positive and negative dictionaries
    positive_dictionary = load_master_dictionary(
        MASTER_DIR / "positive-words.txt"
    )

    negative_dictionary = load_master_dictionary(
        MASTER_DIR / "negative-words.txt"
    )

    # Exclude custom stopwords from both dictionaries
    positive_dictionary -= custom_stopwords
    negative_dictionary -= custom_stopwords

    print("Custom stopwords loaded:", len(custom_stopwords))
    print("NLTK stopwords loaded:", len(nltk_stopwords))
    print("Positive words loaded:", len(positive_dictionary))
    print("Negative words loaded:", len(negative_dictionary))

    # Read validated input URLs
    dataframe = pd.read_excel(INPUT_FILE)

    # Test mode
    if TEST_LIMIT is not None:
        dataframe = dataframe.head(TEST_LIMIT)

    # Define exact output column order
    output_columns = [
    "URL_ID",
    "URL",
    "POSITIVE SCORE",
    "NEGATIVE SCORE",
    "POLARITY SCORE",
    "SUBJECTIVITY SCORE",
    "AVG SENTENCE LENGTH",
    "PERCENTAGE OF COMPLEX WORDS",
    "FOG INDEX",
    "AVG NUMBER OF WORDS PER SENTENCE",
    "COMPLEX WORD COUNT",
    "WORD COUNT",
    "SYLLABLE PER WORD",
    "PERSONAL PRONOUNS",
    "AVG WORD LENGTH"
]

    results = []
    skipped_ids = []

    print("\nArticles to analyse:", len(dataframe))

    # Process articles
    for _, row in dataframe.iterrows():

        url_id = int(row["URL_ID"])
        url = row["URL"]

        article_path = ARTICLES_DIR / f"{url_id}.txt"

        print("\nProcessing URL_ID:", url_id)

        if not article_path.exists():

            print("Article file not found:", url_id)
            skipped_ids.append(url_id)
            continue

        # Read article text
        article_text = article_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        # Calculate all 13 variables
        metrics = calculate_metrics(
            article_text,
            custom_stopwords,
            positive_dictionary,
            negative_dictionary,
            nltk_stopwords
        )

        # Add input variables first
        result = {
            "URL_ID": url_id,
            "URL": url
        }

        result.update(metrics)

        results.append(result)

        print("Positive Score:", metrics["POSITIVE SCORE"])
        print("Negative Score:", metrics["NEGATIVE SCORE"])
        print("Word Count:", metrics["WORD COUNT"])

    # Create output DataFrame in exact template order
    output_dataframe = pd.DataFrame(
        results,
        columns=output_columns
    )

    # Save output Excel file
    output_dataframe.to_excel(
        OUTPUT_FILE,
        index=False
    )

    # Final report
    print("\n======================================")
    print("TEXT ANALYSIS COMPLETED")
    print("======================================")

    print("Articles analysed:", len(results))
    print("Articles skipped:", len(skipped_ids))
    print("Output rows:", len(output_dataframe))
    print("Output file:", OUTPUT_FILE)

    if skipped_ids:
        print("Skipped URL_IDs:", skipped_ids)


# ==================================================
# 7. PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()
