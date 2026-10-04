from ia.guardrails.intent import IntentClassifier, QueryIntent


def test_intent_classifier_universal():
    assert IntentClassifier.classify("") == QueryIntent.CHITCHAT_GREETING
    assert IntentClassifier.classify("   ") == QueryIntent.CHITCHAT_GREETING
    assert IntentClassifier.classify("Olá, bom dia!") == QueryIntent.KNOWLEDGE_QUERY
    assert IntentClassifier.classify("Qual é o meu nome ?") == QueryIntent.KNOWLEDGE_QUERY
    assert IntentClassifier.classify("Leina lame ke mang?") == QueryIntent.KNOWLEDGE_QUERY
    assert IntentClassifier.classify("Como tirar CPF?") == QueryIntent.KNOWLEDGE_QUERY
