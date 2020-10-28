import random

from grandpy.parser import Parser
from grandpy.apis.googlemaps import GoogleGeocodingClient, GoogleGeocodingError
from grandpy.apis.wikipedia import WikipediaClient, WikipediaError


positive_answers = [
    "Bien sûr mon poussin ! Voici ce que tu cherches :",
    "J'ai trouvé ce que tu cherches ! Voici les infos qui t'intéressent :",
    "Je savais que je connaissais cet endroit ! Voici ce que j'en sais :",
    "C'est bien parce que c'est toi ! Voici ce l'adresse :",
]

negative_answers = [
    "A mon âge, on n'entend plus très bien. Pourrais-tu répéter plus fort ?",
    "Mes oreilles ne sont plus de toute jeunesse, peux-tu répéter ?",
    "Je n'ai pas compris ta question, peux-tu reformuler ?",
]

article_intros = [
    "Au fait, cela me rappelle :",
    "Mes souvenir datent un peu, mais voici ce dont je me souvient :",
    "Je me rappelle de ceci, ça peut t'intéresser :",
    "Voici ce que la mémoire d'un vieille homme vieillissant peut ajouter :",
]


def answer(question):
    """Answer the question passed as an argument in a conversational mode."""
    parser = Parser()
    google_client = GoogleGeocodingClient()
    wikipedia_client = WikipediaClient()

    # Utilisation du parser et des clients d'APIs
    try:
        cleaned_question = parser.parse(question)
        geo_info = google_client.search(cleaned_question)
        pages = wikipedia_client.geosearch(
            latitude=geo_info["latitude"], longitude=geo_info["longitude"]
        )
    except (GoogleGeocodingError, WikipediaError):
        return {"found": False, "answer": random.choice(negative_answers)}

    # Préparation de la réponse
    return {
        "found": True,
        "answer": random.choice(positive_answers),
        "intro": random.choice(article_intros),
        **geo_info,
        **pages[0].as_dict(),
    }
