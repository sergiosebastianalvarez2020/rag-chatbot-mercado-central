# 🤖 Agente IA - Mercado Central 24h

Proyecto desarrollado como Challenge Final de Alura.

Este agente utiliza Inteligencia Artificial y técnicas de Retrieval-Augmented Generation (RAG) para responder preguntas en lenguaje natural sobre un documento PDF de preguntas frecuentes de Mercado Central 24h.

---

# Tecnologías utilizadas

- Python
- Google Gemini Flash Lite
- LangChain
- ChromaDB
- Sentence Transformers
- HuggingFace Embeddings
- PyPDF

---

# Arquitectura

El flujo del proyecto es el siguiente:

1. Se carga un documento PDF.
2. El documento se divide en bloques de preguntas y respuestas.
3. Se generan embeddings utilizando un modelo multilingüe de Sentence Transformers.
4. Los embeddings se almacenan en una base vectorial ChromaDB.
5. Cuando el usuario realiza una pregunta:
   - se buscan los fragmentos más relevantes del documento;
   - esos fragmentos se envían como contexto a Gemini;
   - Gemini genera una respuesta utilizando únicamente la información recuperada.

Además, el chatbot mantiene memoria de la conversación para responder correctamente preguntas relacionadas con mensajes anteriores.

---

# Características

- Lectura automática de documentos PDF.
- Búsqueda semántica mediante embeddings.
- Base vectorial persistente con ChromaDB.
- Memoria de conversación.
- Respuestas generadas mediante Google Gemini.
- Arquitectura RAG (Retrieval-Augmented Generation).

---

# Ejemplos

Pregunta:

> ¿El estacionamiento es gratis?

Respuesta:

> El estacionamiento es gratuito durante las primeras 2 horas para clientes que presenten un ticket de compra...

Pregunta:

> ¿Y después cuánto cuesta?

Respuesta:

> Luego del período de cortesía se aplica la tarifa comercial vigente.

---

# Instalación

Crear un entorno virtual:

```bash
python -m venv venv
```

Activarlo:

Windows

```bash
venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear un archivo `.env` con la API Key de Gemini.

Ejecutar:

```bash
python app_vectores.py
```

---

# Autor

Sebastián Álvarez

Challenge Final — Alura