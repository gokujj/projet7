import os

from flask import Flask, request, jsonify, render_template

from grandpy.bot import answer

app = Flask(__name__)


@app.route("/")
def homepage_view():
    """View managing the request to obtain the home page of the site."""
    return render_template(
        "home.html", key=os.getenv("GOOGLE_MAPS_JAVASCRIPT_KEY")
    )


@app.route("/question", methods=["POST"])
def question_view():
    """View managing the request to obtain an answer to a question in
     processing ajax requests from javascript.
    """
    question = request.form["question"]
    response = answer(question)
    return jsonify(response)
