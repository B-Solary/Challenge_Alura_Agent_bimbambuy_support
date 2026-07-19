"""
Envía un registro (log) de cada pregunta/respuesta a un endpoint de Oracle
APEX/ORDS (Oracle Autonomous Database). Esto cumple el requisito de usar al
menos un servicio de OCI, sin necesidad de correr toda la app dentro de una
VM de OCI Compute.

Si OCI_LOG_ENDPOINT no está configurado, o si falla la conexión, el agente
sigue funcionando con normalidad: el registro es "mejor esfuerzo" y nunca
bloquea ni rompe una respuesta al usuario.
"""

import os
import time
import requests


def log_interaction(question: str, answer: str, sources=None):
    endpoint = os.getenv("OCI_LOG_ENDPOINT")
    if not endpoint:
        return  # logging deshabilitado: no pasa nada, la app sigue normal

    payload = {
        "question": question,
        "answer": answer,
        "sources": ", ".join(sources or []),
        "timestamp": int(time.time()),
    }

    try:
        requests.post(endpoint, json=payload, timeout=3)
    except requests.RequestException:
        # Si el servicio de OCI no responde, no interrumpimos al usuario.
        pass
