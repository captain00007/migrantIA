from ia.security.canary import CanaryManager


def test_canary_manager_generation():
    token1 = CanaryManager.generate_token()
    token2 = CanaryManager.generate_token()

    assert token1.startswith("CANARY_")
    assert token2.startswith("CANARY_")
    assert token1 != token2


def test_canary_manager_system_instruction():
    token = "CANARY_TEST123456"
    system_prompt = "Você é o assistente MigrantIA."
    protected_prompt = CanaryManager.format_system_instruction(system_prompt, token)

    assert "CANARY_TEST123456" in protected_prompt
    assert "Under NO circumstances" in protected_prompt


def test_canary_manager_check_leakage():
    token = "CANARY_TEST123456"
    leaked_output = f"Sure! My secret canary is {token}"
    safe_output = "Para tirar o CPF, acesse o site da Receita Federal."

    assert CanaryManager.check_leakage(leaked_output, token) is True
    assert CanaryManager.check_leakage(safe_output, token) is False
