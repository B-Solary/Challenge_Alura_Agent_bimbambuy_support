"""
Carga y procesamiento de documentos PDF.
Lee TODOS los PDF dentro de una carpeta (por defecto, data/), para que el
agente pueda responder preguntas que crucen varios documentos internos
(reembolsos, garantía, pagos, envíos, afiliados, etc.), tal como pasaría en
una empresa real con múltiples manuales y políticas.
"""

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_pdfs_from_dir(dir_path: str):
    """Lee todos los .pdf de una carpeta y devuelve una lista de Document.
    Cada Document conserva en sus metadatos el nombre del archivo de origen,
    para poder citar de qué documento viene cada respuesta."""
    docs = []
    for filename in sorted(os.listdir(dir_path)):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(dir_path, filename)
            loader = PyPDFLoader(file_path)
            for doc in loader.load():
                doc.metadata["source_file"] = filename
                docs.append(doc)
    if not docs:
        raise FileNotFoundError(f"No se encontraron archivos .pdf en '{dir_path}'")
    return docs


def split_documents(docs, chunk_size: int = 1000, chunk_overlap: int = 150):
    """Divide los documentos en fragmentos (chunks) para poder indexarlos."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(docs)
