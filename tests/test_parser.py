import string
import json

from grandpy import parser

accents = [
    "à",
    "ä",
    "â",
    "é",
    "è",
    "ê",
    "ë",
    "ò",
    "ô",
    "ö",
    "ï",
    "î",
    "ì",
    "û",
    "ù",
    "ü",
    "ç",
]


def test_transform_to_lowercase_removes_all_uppercase_letters():
    cleaned = parser.transform_to_lowercase(string.ascii_uppercase)
    for i, (lower, upper) in enumerate(
        zip(string.ascii_uppercase, string.ascii_lowercase)
    ):
        assert cleaned[i] != string.ascii_uppercase[i]
        assert cleaned[i] == string.ascii_lowercase[i]


def test_transforms_nothing_if_all_lowercase():
    cleaned = parser.transform_to_lowercase(string.ascii_lowercase)
    assert cleaned == string.ascii_lowercase


def test_remove_all_accents_removes_all_french_accents():
    cleaned = parser.remove_all_accents("".join(accents))
    for accent in accents:
        assert accent not in cleaned


def test_remove_all_accents_removes_nothing_if_no_accent_present():
    cleaned = parser.remove_all_accents(string.printable)
    assert cleaned == string.printable


def test_normalize_spaces_removes_multiple_spaces_in_sentence():
    cleaned = parser.normalize_spaces("salut    grandpy,    comment va ?")
    assert "  " not in cleaned


def test_normalize_spaces_changes_nothing_if_no_multiple_space_present():
    sentence = "salut grandpy, comment va ?"
    cleaned = parser.normalize_spaces(sentence)
    assert sentence == cleaned


def test_extract_places_extracts_places_correctly():
    with open("data/questions.json") as jsonfile:
        question_tags = json.load(jsonfile)
    for question_tag in question_tags:
        sentence = f"avant {question_tag}après"
        cleaned = parser.extract_place(sentence)
        assert cleaned == "après"


def test_extract_places_does_nothing_if_no_question_tag_is_present():
    cleaned = parser.extract_place("avant après")
    assert cleaned == "avant après"


def test_remove_all_apostrophes_works_correctly():
    cleaned = parser.remove_apostrophes("l'enfer, d'enfer")
    assert cleaned == "l enfer, d enfer"


def test_remove_all_apostrophe_removes_nothing_if_no_apostrophe():
    sentence = "Bienvenue chez openclassrooms"
    cleaned = parser.remove_apostrophes(sentence)
    assert cleaned == sentence


def test_remove_punctuation_characters_removes_all_non_ascii_letters():
    cleaned = parser.remove_punctuation_characters(",:.;!?-")
    assert cleaned == "-"


def test_remove_punctuation_removes_nothing_if_not_punctuation():
    sentence = "Une phrase sans ponctuation"
    cleaned = parser.remove_punctuation_characters(sentence)
    assert cleaned == sentence


def test_remove_stop_words_removes_stop_words():
    with open("data/fr.json") as jsonfile:
        stop_words = json.load(jsonfile)
    sentence = " ".join(stop_words)
    cleaned = parser.remove_stop_words(sentence)
    assert cleaned.strip() == ""


def test_remove_stop_words_does_nothing_if_not_stop_word_is_present():
    sentence = "pasunstopword pasunstopword pasunstopword"
    cleaned = parser.remove_stop_words(sentence)
    assert sentence == cleaned


def test_parser_removes_uppercase():
    parser_object = parser.Parser()
    cleaned = parser_object.parse(string.ascii_letters)
    for letter in string.ascii_uppercase:
        assert letter not in cleaned


def test_parser_removes_accents():
    parser_object = parser.Parser()
    cleaned = parser_object.parse("".join(accents))
    for accent in accents:
        assert accent not in cleaned


def test_parser_places_extracts_places_correctly():
    parser_object = parser.Parser()
    with open("data/questions.json") as jsonfile:
        question_tags = json.load(jsonfile)
    for question_tag in question_tags:
        sentence = f"introductiondequestion {question_tag}lieurecherche"
        cleaned = parser_object.parse(sentence)
        assert cleaned == "lieurecherche"


def test_parse_removes_stop_words():
    parser_object = parser.Parser()
    with open("data/fr.json") as jsonfile:
        stop_words = json.load(jsonfile)
    sentence = " ".join(stop_words)
    cleaned = parser_object.parse(sentence)
    assert cleaned.strip() == ""


def test_remove_stop_words_does_nothing_if_not_stop_word_is_present():
    sentence = "pasunstopword pasunstopword pasunstopword"
    cleaned = parser.remove_stop_words(sentence)
    assert sentence == cleaned
