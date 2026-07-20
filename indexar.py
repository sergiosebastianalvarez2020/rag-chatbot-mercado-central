from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

import re
import shutil
import os

RUTA_PDF = "documentos/preguntas frecuentes- mercado central.pdf"
CHROMA_DIR = "chroma_db"

# ==========================
# REEMPLAZAR BASE
# ==========================

if os.path.exists(CHROMA_DIR):

    respuesta = input(
        "La base vectorial ya existe. ¿Desea reemplazarla? (s/n): "
    )

    if respuesta.lower() == "s":

        shutil.rmtree(CHROMA_DIR)

    else:

        print("Operación cancelada.")

        exit()

# ==========================
# CARGAR PDF
# ==========================

loader = PyPDFLoader(RUTA_PDF)

documentos = loader.load()

print(
    f"PDF cargado ({len(documentos)} páginas)"
)

texto = "\n".join(
    doc.page_content
    for doc in documentos
)

bloques = re.split(
    r'(?=¿)',
    texto
)

faq_docs = []

for bloque in bloques:

    bloque = bloque.strip()

    if "¿" in bloque and len(bloque) > 100:

        faq_docs.append(
            Document(
                page_content=bloque
            )
        )

print(
    f"FAQs encontradas: {len(faq_docs)}"
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

Chroma.from_documents(
    documents=faq_docs,
    embedding=embeddings,
    persist_directory=CHROMA_DIR
)

print(
    "Base vectorial creada correctamente."
)