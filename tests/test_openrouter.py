import pytest

from codemind.llm.openrouter import OpenRouterClient


@pytest.fixture(autouse=True)
def prevent_dotenv_loading(monkeypatch):
    """Prevent the real .env file from affecting unit tests."""

    monkeypatch.setattr(
        "codemind.llm.openrouter.load_dotenv",
        lambda *args, **kwargs: False,
    )


def test_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")

    with pytest.raises(ValueError, match="API_KEY"):
        OpenRouterClient()


def test_client_requires_model(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)

    with pytest.raises(ValueError, match="MODEL"):
        OpenRouterClient()


def test_rejects_empty_messages():
    client = OpenRouterClient(
        api_key="test-key",
        model="test-model",
    )

    with pytest.raises(ValueError, match="Messages"):
        client.generate([])


def test_rejects_invalid_temperature():
    client = OpenRouterClient(
        api_key="test-key",
        model="test-model",
    )

    with pytest.raises(ValueError, match="Temperature"):
        client.generate(
            [{"role": "user", "content": "Hello"}],
            temperature=3,
        )


def test_rejects_invalid_max_tokens():
    client = OpenRouterClient(
        api_key="test-key",
        model="test-model",
    )

    with pytest.raises(ValueError, match="max_tokens"):
        client.generate(
            [{"role": "user", "content": "Hello"}],
            max_tokens=0,
        )
