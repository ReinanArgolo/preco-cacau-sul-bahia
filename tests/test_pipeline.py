from cocoa_data.pipeline import sanitize_public_message


def test_public_source_message_removes_urls_and_secrets() -> None:
    message = "GET https://example.test/path?token=abc password=hunter2 falhou"
    cleaned = sanitize_public_message(message)
    assert "https://" not in cleaned
    assert "hunter2" not in cleaned
