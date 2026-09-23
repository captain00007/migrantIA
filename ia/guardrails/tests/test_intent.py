from ia.guardrails.intent import IntentClassifier, QueryIntent


def test_intent_classifier_empty_and_valid_queries():
    assert IntentClassifier.classify("") == QueryIntent.CHITCHAT_GREETING
    assert IntentClassifier.classify("   ") == QueryIntent.CHITCHAT_GREETING
    assert IntentClassifier.classify("Como tirar CPF?") == QueryIntent.KNOWLEDGE_QUERY
    assert IntentClassifier.classify("Olá, bom dia!") == QueryIntent.KNOWLEDGE_QUERY
    assert IntentClassifier.classify("me diga sobre o que pode falar") == QueryIntent.KNOWLEDGE_QUERY
