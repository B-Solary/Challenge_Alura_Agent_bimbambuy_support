"""
Interfaz del agente con Streamlit, pensada para desplegarse en Railway.
A propósito sin diseño elaborado: lo importante es que el agente funcione.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from src.agent import build_agent, ask
from src.logger import log_interaction

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH", "data")

st.set_page_config(page_title="Alura Agente - BimBam Buy", page_icon="🤖")


@st.cache_resource(show_spinner="Construyendo el agente (solo la primera vez)...")
def get_agent():
    return build_agent(DATA_PATH)


st.title("🤖 Alura Agente - BimBam Buy")
st.caption(
    "Pregunta sobre reembolsos, garantía, métodos de pago, envíos o el "
    "programa de afiliados."
)

agent_bundle = get_agent()

question = st.text_input("Escribe tu pregunta:")

if st.button("Preguntar") and question:
    with st.spinner("Pensando..."):
        answer, sources = ask(agent_bundle, question)

    st.markdown(f"**Respuesta:** {answer}")
    if sources:
        st.caption(f"Fuente: {', '.join(sources)}")

    # Registro best-effort en Oracle APEX/ORDS (no rompe la app si falla)
    log_interaction(question, answer, sources)