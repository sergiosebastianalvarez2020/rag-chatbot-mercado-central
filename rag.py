from config import cliente
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv
import os

load_dotenv()
from langchain_chroma import Chroma
# ==========================
# VECTOR STORE
# ==========================

def cargar_retriever():

    embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )

    return vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )


retriever = None

# ==========================
# MEMORIA
# ==========================

historial = []

# ==========================
# FUNCIONES
# ==========================

def buscar_contexto(pregunta_busqueda):

    resultados = retriever.invoke(
        pregunta_busqueda
    )

    return "\n\n".join(
        doc.page_content
        for doc in resultados
    )


def construir_historial():

    texto = ""

    for pregunta, respuesta in historial:

        texto += (
            f"Usuario: {pregunta}\n"
            f"Bot: {respuesta}\n\n"
        )

    return texto


def crear_prompt(
    contexto,
    historial_texto,
    pregunta
):

    return f"""
Eres un asistente virtual de Mercado Central 24h.

Responde únicamente utilizando la información del CONTEXTO.

Puedes utilizar el historial solamente para comprender referencias.

Si la respuesta no está en el contexto responde exactamente:

"No tengo esa información en el contexto proporcionado."

No inventes datos.

HISTORIAL:
{historial_texto}

CONTEXTO:
{contexto}

PREGUNTA:
{pregunta}

RESPUESTA:
"""


def consultar_gemini(prompt):

    try:

        respuesta = cliente.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt
        )

        return respuesta.text

    except Exception as e:
       print("ERROR GEMINI:", e)
       raise


def preguntar(pregunta):

    global retriever

    if retriever is None:
        print("Cargando retriever...")
        retriever = cargar_retriever()

    

    if historial:

        pregunta_busqueda = (
            historial[-1][0]
            + " "
            + pregunta
            + " Mercado Central 24h"
        )

    else:

        pregunta_busqueda = (
            pregunta
            + " Mercado Central 24h"
        )

    # ==========================
    # MEDIR CHROMA
    # ==========================

    inicio = time.time()

    contexto = buscar_contexto(
        pregunta_busqueda
    )

    print(
        f"Buscar contexto: {time.time() - inicio:.2f} segundos"
    )

    historial_texto = construir_historial()

    prompt = crear_prompt(
        contexto,
        historial_texto,
        pregunta
    )

    # ==========================
    # MEDIR GEMINI
    # ==========================

    inicio = time.time()

    respuesta = consultar_gemini(
        prompt
    )

    print(
        f"Gemini respondió en: {time.time() - inicio:.2f} segundos"
    )

    historial.append(
        (
            pregunta,
            respuesta
        )
    )

    if len(historial) > 6:
        historial.pop(0)

    return respuesta