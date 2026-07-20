from flask import Flask, render_template, request
from rag import preguntar, historial

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def inicio():

    if request.method == "POST":

        pregunta = request.form["pregunta"]

        preguntar(pregunta)

    return render_template(
        "index.html",
        historial=historial
    )


if __name__ == "__main__":
    app.run(debug=True)