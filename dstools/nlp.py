import string
import unicodedata

import nltk
import inflect
import bs4 as BeautifulSoup


# inflection engine
p = inflect.engine()

# lemmatizer
lemmatizer = nltk.WordNetLemmatizer()


def get_stopwords(lang="english", additional_stopwords=[]):
    """
    returns a set of unique stopwords
    """
    stopwords = set(nltk.corpus.stopwords.words(lang))
    if len(additional_stopwords) > 0:
        stopwords |= set(additional_stopwords)

    return stopwords


def strip(words):
    """
    strip words
    """
    if isinstance(words, str):
        words = [words]

    return [
        word.strip()
        for word in words
        if word.strip() != ""
    ]


def lowercase(words):
    """
    lowercase all words
    """
    if isinstance(words, str):
        words = [words]

    return [
        word.lower()
        for word in words
    ]


def remove_punctuation(words):
    """
    remove the punctuation from words
    """
    if isinstance(words, str):
        words = [words]

    # translation table to map punctuations to None
    punctuation_table = str.maketrans(dict.fromkeys(string.punctuation))

    return [
        word.translate(punctuation_table)
        for word in words
    ]


def remove_non_ascii(words):
    """
    remove all non ascii characters from words
    """
    if isinstance(words, str):
        words = [words]

    return [
        unicodedata.normalize("NFKD", word).encode(
            "ascii", "ignore"
        ).decode("utf-8", "ignore")
        for word in words
    ]


def remove_html(words):
    """
    remove all HTML tags
    """
    if isinstance(words, str):
        words = [words]

    return [
        BeautifulSoup.BeautifulSoup(word, "html.parser").text
        for word in words
    ]


def replace_numbers(words):
    """
    replace numbers to words
    """
    if isinstance(words, str):
        words = [words]

    return [
        p.number_to_words(word) if word.isdigit() else word
        for word in words
    ]


def remove_stopwords(words, stopwords):
    """
    removes all stop words
    """
    assert(len(stopwords) > 0)

    if isinstance(words, str):
        words = [words]

    return [
        word
        for word in words
        if word not in stopwords
    ]


def stem(words, stemmer_class=nltk.PorterStemmer):
    """
    stem the words
    """
    if isinstance(words, str):
        words = [words]

    stemmer = stemmer_class()
    return [
        stemmer.stem(word)
        for word in words
    ]


def lemmatize(words, pos="v"):
    """
    lemmatize the words
    """
    if isinstance(words, str):
        words = [words]

    return [
        lemmatizer.lemmatize(word, pos)
        for word in words
    ]


def normalize(
    words, do_strip=True, do_lowercase=True, do_remove_non_ascii=True,
    do_remove_punctuation=True, do_remove_html=True,
    do_replace_numbers=True, do_remove_stopwords=True,
    stopwords=get_stopwords()
):
    """
    normalize given words
    """
    if do_remove_html:
        words = remove_html(words)

    if do_remove_non_ascii:
        words = remove_non_ascii(words)

    if do_lowercase:
        words = lowercase(words)

    if do_remove_punctuation:
        words = remove_punctuation(words)

    if do_replace_numbers:
        words = replace_numbers(words)

    if do_remove_stopwords:
        words = remove_stopwords(words, stopwords)

    if do_strip:
        words = strip(words)

    return words
