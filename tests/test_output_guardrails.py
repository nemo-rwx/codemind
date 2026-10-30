import pytest

from codemind.agent.output_guardrails import OutputGuardrails


def test_accepts_normal_answer():
    guardrails = OutputGuardrails()

    answer = "Repository indexing is handled by RepositoryIndexer."

    assert guardrails.validate(answer) == answer


def test_redacts_secret_from_answer():
    guardrails = OutputGuardrails()

    answer = "The API key is api_key = 'abcdefghijklmnop123456'"

    result = guardrails.validate(answer)

    assert "abcdefghijklmnop123456" not in result
    assert "[REDACTED]" in result


def test_rejects_empty_answer():
    guardrails = OutputGuardrails()

    with pytest.raises(ValueError):
        guardrails.validate(" ")


def test_rejects_non_string_answer():
    guardrails = OutputGuardrails()

    with pytest.raises(ValueError):
        guardrails.validate(None)
