"""
Módulo de Logging Seguro e Auditoria LGPD.
Registra eventos de segurança e telemetria sem expor PII nem conteúdo sensível.
"""
import hashlib
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("migrantia.security")


def log_security_event(
    event_type: str,
    session_id: Optional[str] = None,
    raw_input: Optional[str] = None,
    reason: Optional[str] = None,
    step: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Registra um evento de segurança em log estruturado.
    Garante anonimato total: o input do usuário é armazenado apenas como hash SHA-256 parcial.
    """
    input_hash = None
    input_length = 0
    if raw_input:
        input_length = len(raw_input)
        input_hash = hashlib.sha256(raw_input.encode("utf-8")).hexdigest()[:16]

    log_payload = {
        "event_type": event_type,
        "session_id": str(session_id) if session_id else "anonymous",
        "input_hash": input_hash,
        "input_length": input_length,
        "reason": reason or "N/A",
        "step": step,
        "extra_metadata": metadata or {},
    }

    logger.warning("MIGRANTIA_SECURITY_EVENT: %s", log_payload)
