from apps.chat.privacy import sanitize_pii, has_pii


def test_has_pii_detection():
    assert has_pii("Meu CPF é 123.456.789-00") is True
    assert has_pii("Contato pelo email maria@gmail.com") is True
    assert has_pii("Telefone (11) 98765-4321") is True
    assert has_pii("Passaporte BR123456") is True
    assert has_pii("Como faço para tirar a carteira de trabalho no Brasil?") is False


def test_sanitize_cpf():
    text = "Meu CPF é 123.456.789-00 e do meu filho 98765432100"
    sanitized = sanitize_pii(text)
    assert "123.456.789-00" not in sanitized
    assert "[CPF_REDACTED]" in sanitized


def test_sanitize_email_and_phone():
    text = "Fale comigo em jose@migrante.org ou no 11988887777"
    sanitized = sanitize_pii(text)
    assert "jose@migrante.org" not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "[PHONE_REDACTED]" in sanitized


def test_sanitize_clean_text():
    clean = "Gostaria de saber onde fica a Defensoria Pública da União em São Paulo."
    assert sanitize_pii(clean) == clean
