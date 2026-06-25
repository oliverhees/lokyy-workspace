"""M2.3: self-improvement — fact extraction (parsing + LLM via mock)."""
from app.core import learning_service, llm


def _cfg():
    return llm.LLMConfig(base_url="http://x/v1", model="m", api_key="k", provider="openai")


def test_parse_trims_filters_and_caps():
    out = learning_service._parse('{"facts": [" Heißt Oliver ", "", "Ist Designer"]}')
    assert out == ["Heißt Oliver", "Ist Designer"]
    # garbage / no JSON → empty
    assert learning_service._parse("kein json") == []
    assert learning_service._parse('{"nope": 1}') == []
    # caps at the max number of facts
    big = '{"facts": [' + ",".join(f'"f{i}"' for i in range(20)) + "]}"
    assert len(learning_service._parse(big)) == learning_service._MAX_FACTS


async def test_extract_facts_via_mock():
    facts = await learning_service.extract_facts(
        "Ich heiße Oliver und bin selbstständiger Designer.", "Freut mich!", _cfg(),
        mock_response='{"facts": ["Heißt Oliver", "Selbstständiger Designer"]}',
    )
    assert facts == ["Heißt Oliver", "Selbstständiger Designer"]


async def test_extract_facts_handles_non_json_response():
    facts = await learning_service.extract_facts(
        "Hallo", "Hi", _cfg(), mock_response="Ich habe nichts Dauerhaftes gefunden.",
    )
    assert facts == []
