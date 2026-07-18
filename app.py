from config import cliente
from flask import Flask, render_template, request

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

import re
import os
app = Flask(__name__)

# ==========================
# CARGAR PDF
# ==========================

RUTA_PDF = "documentos/preguntas frecuentes- mercado central.pdf"

loader = PyPDFLoader(RUTA_PDF)

documentos = loader.load()

print("PDF cargado")
print("Páginas:", len(documentos))


# ==========================
# UNIR TEXTO DEL PDF
# ==========================

texto_completo = "\n".join(
    [doc.page_content for doc in documentos]
)


# ==========================
# CREAR BLOQUES FAQ
# ==========================

bloques = re.split(r'(?=¿)', texto_completo)

faq_limpio = []

for bloque in bloques:
    bloque = bloque.strip()

    if "¿" in bloque and len(bloque) > 100:
        faq_limpio.append(bloque)


print("Bloques FAQ:", len(faq_limpio))


# ==========================
# CREAR VECTOR STORE
# ==========================

faq_docs = [
    Document(page_content=faq)
    for faq in faq_limpio
]
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
CHROMA_DIR = "chroma_db"

if os.path.exists(CHROMA_DIR):

    print("Cargando base vectorial...")

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

else:

    print("Creando base vectorial...")

    vectorstore = Chroma.from_documents(
        documents=faq_docs,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)



def preguntar(pregunta):

    # Si hay historial, usar la última pregunta para mejorar la búsqueda
    if historial:
        ultima_pregunta = historial[-1][0]
        pregunta_busqueda = f"{ultima_pregunta} {pregunta} Mercado Central 24h"
    else:
        pregunta_busqueda = f"{pregunta} Mercado Central 24h"

    resultados = retriever.invoke(pregunta_busqueda)

    contexto = "\n\n".join(
        [doc.page_content for doc in resultados]
    )

    historial_texto = ""

    for pregunta_anterior, respuesta_anterior in historial:
        historial_texto += f"Usuario: {pregunta_anterior}\n"
        historial_texto += f"Bot: {respuesta_anterior}\n\n"

    prompt = f"""
Eres un asistente de Mercado Central 24h.

Responde únicamente usando la información del contexto.
Puedes utilizar el historial de la conversación para entender a qué se refiere el usuario.

Si la información no está en el contexto, indica que no tienes esa información.
No inventes datos.

HISTORIAL:
{historial_texto}

CONTEXTO:
{contexto}

PREGUNTA ACTUAL:
{pregunta}

RESPUESTA:
"""

    respuesta = cliente.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt
    )

    respuesta_texto = respuesta.text

    historial.append((pregunta, respuesta_texto))

    if len(historial) > 10:
        historial.pop(0)

    return respuesta_texto
# ==========================
# MEMORIA DE LA CONVERSACIÓN
# ==========================

historial = []

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