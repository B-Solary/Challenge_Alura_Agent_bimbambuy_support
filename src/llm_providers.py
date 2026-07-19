"""
Aquí elegimos qué "cerebro" (LLM) usa el agente, según la variable de
entorno LLM_PROVIDER. Así puedes cambiar de proveedor sin tocar el resto
del código: solo edita tu archivo .env
"""

import os


def get_embeddings():
    """
    Embeddings locales y gratuitos (no requieren API key ni conexión).
    """
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def get_llm():
    """
    Devuelve el LLM configurado según LLM_PROVIDER.
    Valores soportados: openai | cohere | google | ollama
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    if provider == "cohere":
        from langchain_cohere import ChatCohere
        return ChatCohere(
            model=os.getenv("COHERE_MODEL", "command-r"),
            temperature=0,
            cohere_api_key=os.getenv("COHERE_API_KEY"),
        )

    if provider == "google":
        # Sirve tanto para Gemini como para modelos Gemma expuestos vía API de Google
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL", "gemini-1.5-flash"),
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )

    if provider == "ollama":
        # Para correr Gemma (u otro modelo) 100% local, sin API key
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "gemma2"),
            temperature=0,
        )

    raise ValueError(
        f"LLM_PROVIDER='{provider}' no reconocido. Usa: openai, cohere, google u ollama."
    )
