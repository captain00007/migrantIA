"""
Núcleo de Segurança Defense-in-Depth do MigrantIA.
"""
from ia.security.normalizer import normalize_unicode_input, is_obfuscated_encoding
from ia.security.canary import CanaryManager
from ia.security.output_guard import OutputGuard
from ia.security.context_shield import ContextShield
from ia.security.logging import log_security_event

__all__ = [
    "normalize_unicode_input",
    "is_obfuscated_encoding",
    "CanaryManager",
    "OutputGuard",
    "ContextShield",
    "log_security_event",
]
