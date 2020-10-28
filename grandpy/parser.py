"""Module defining a parser capable of cleaning a question of place
so as to extract the important information to find the address and
geographic coordinates.
"""

import json
import string

# translation table for accents
translations = {
    "à": "a",
    "ä": "a",
    "â": "a",
    "é": "e",
    "è": "e",
    "ê": "e",
    "ë": "e",
    "ò": "o",
    "ô": "o",
    "ö": "o",
    "ï": "i",
    "î": "i",
    "ì": "i",
    "û": "u",
    "ù": "u",
    "ü": "u",
    "ç": "c",
    "\u00e7": "c",
    "\\u00e7": "c",
}


def transform_to_lowercase(sentence):
    """Transform all the characters of the sentence received as an argument into
     lowercase.
    """
    return sentence.lower()


def remove_all_accents(sentence):
    """Removes accents from the sentence passed in arguments."""
    for with_accent, without_accent in translations.items():
        sentence = sentence.replace(with_accent, without_accent)
    return sentence


def normalize_spaces(sentence):
    """Removes unnecessary spaces in the sentence passed as arguments."""
    final_sentence = []
    in_word = False
    for letter in sentence:
        if letter.isspace() and not in_word:
            continue
        elif letter.isspace() and in_word:
            in_word = False
        elif letter.isalpha():
            in_word = True
        final_sentence.append(letter)
    return "".join(final_sentence)


def extract_place(sentence):
    """Extract the location if a location issue is detected."""
    # Loading location questions from json file
    with open("data/questions.json") as jsonfile:
        question_tags = json.load(jsonfile)

    # Extraction
    for question_tag in question_tags:
        parts = sentence.split(question_tag)
        if len(parts) == 2:
            return parts[1]
    return sentence


def remove_apostrophes(sentence):
    """Removes the apostrophes from the sentence passed in parameters."""
    return (
        sentence.replace("'", " ")
        .replace("quelqu un", "quelqu'un")
        .replace("aujourd hui", "aujourd'hui")
    )


def remove_stop_words(sentence):
    """Removes common words from the sentence passed as an argument."""
    # Loading common words from the json file
    with open("data/fr.json") as jsonfile:
        stop_words = set(json.load(jsonfile))  # set() speeds up the operator in

    final_sentence = []
    for word in sentence.split(" "):
        if word not in stop_words:
            final_sentence.append(word)
    return " ".join(final_sentence)


def remove_punctuation_characters(sentence):
    """Removes punctuation."""
    for letter in sentence:
        if letter not in set(string.ascii_letters + string.whitespace + "'-"):
            sentence = sentence.replace(letter, "")
    return sentence


class Parser:
    """Object responsible for cleaning up questions sent by the user
     in order to facilitate research on a geolocation API.
    """

    cleaners = [
        transform_to_lowercase,
        remove_all_accents,
        normalize_spaces,
        extract_place,
        remove_apostrophes,
        remove_stop_words,
        remove_punctuation_characters,
    ]

    def parse(self, sentence):
        """Extract important information from the sentence passed in argument.
        """
        for cleaner in self.cleaners:
            sentence = cleaner(sentence)
        return sentence
