from config import cliente

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ==========================
# VECTOR STORE
# ==========================

def cargar_retriever():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )

    return vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )


retriever = cargar_retriever()

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

    except Exception:

        return (
            "Ocurrió un error al consultar Gemini."
        )


def preguntar(pregunta):

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

    contexto = buscar_contexto(
        pregunta_busqueda
    )

    historial_texto = construir_historial()

    prompt = crear_prompt(
        contexto,
        historial_texto,
        pregunta
    )

    respuesta = consultar_gemini(
        prompt
    )

    historial.append(
        (
            pregunta,
            respuesta
        )
    )

    if len(historial) > 10:
        historial.pop(0)

    return respuesta