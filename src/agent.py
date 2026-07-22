"""
Construye el agente sobre TODOS los PDF de la carpeta data/ (o sobre un
CSV, si defines DATA_FILE apuntando a un .csv puntual).

- Varios PDF -> RAG: se trocean todos juntos, se generan embeddings y se
  guardan en un único índice FAISS. Así el agente puede responder
  preguntas que toquen más de un documento (por ejemplo, un caso de
  garantía que también involucra la política de devoluciones).
- Un CSV -> agente pandas: el LLM escribe y ejecuta código pandas sobre tu
  DataFrame. Útil para preguntas analíticas ("¿cuál fue el producto más
  vendido en diciembre de 2015?").
"""

import os
import pandas as pd

from src.llm_providers import get_embeddings, get_llm

INDEX_PATH = "faiss_index"
DATA_DIR = "data"


def build_agent(data_path: str = DATA_DIR, force_rebuild: bool = False):
    llm = get_llm()

    # Si apunta a un único archivo CSV, usamos el agente pandas
    if os.path.isfile(data_path) and data_path.lower().endswith(".csv"):
        return _build_csv_agent(data_path, llm)

    # En cualquier otro caso, tratamos data_path como carpeta con PDFs
    return _build_pdf_agent(data_path, llm, force_rebuild)


def _build_csv_agent(file_path, llm):
    # allow_dangerous_code=True porque el agente ejecuta código pandas real.
    # Está bien para este proyecto de aprendizaje; en producción se debería
    # correr en un entorno aislado (sandbox).
    from langchain_experimental.agents import create_pandas_dataframe_agent

    df = pd.read_csv(file_path)
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        allow_dangerous_code=True,
    )
    return {"type": "csv", "runnable": agent}


def _build_pdf_agent(dir_path, llm, force_rebuild):
    from langchain_classic.chains import RetrievalQA
    from langchain_community.vectorstores import FAISS
    from src.loader import load_pdfs_from_dir, split_documents

    embeddings = get_embeddings()

    if os.path.exists(INDEX_PATH) and not force_rebuild:
        vectorstore = FAISS.load_local(
            INDEX_PATH, embeddings, allow_dangerous_deserialization=True
        )
    else:
        docs = load_pdfs_from_dir(dir_path)
        chunks = split_documents(docs)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(INDEX_PATH)

    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
    )
    return {"type": "pdf", "runnable": qa_chain}


def ask(agent_bundle, question: str):
    """Hace una pregunta al agente y devuelve (respuesta, fuentes)."""
    if agent_bundle["type"] == "csv":
        result = agent_bundle["runnable"].invoke({"input": question})
        return result["output"], []

    result = agent_bundle["runnable"].invoke({"query": question})
    sources = sorted({
        d.metadata.get("source_file", "desconocido")
        for d in result.get("source_documents", [])
    })
    return result["result"], sources
