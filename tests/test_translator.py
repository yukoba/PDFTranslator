from unittest.mock import patch, MagicMock

import fitz  # PyMuPDF
import pytest

from translator import Translator


# Create a simple dummy PDF for testing
def create_dummy_pdf() -> bytes:
    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


@pytest.fixture
def dummy_pdf():
    return create_dummy_pdf()


def test_translator_init_invalid_model():
    with pytest.raises(ValueError):
        Translator(model_type="invalid-model", api_key="test_key")  # type: ignore


@patch("translator.OpenAI")
def test_translator_gpt_call(mock_openai, dummy_pdf):
    # Setup mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is a mock translation from GPT."
    mock_client.chat.completions.create.return_value = mock_response

    # Initialize and translate
    translator = Translator(model_type="gpt-5.4-mini", api_key="test_key")
    result = translator.translate_page(dummy_pdf, target_language="Japanese")

    # Assertions
    assert result == "This is a mock translation from GPT."
    mock_client.chat.completions.create.assert_called_once()

    # Check if prompt was passed correctly
    call_args = mock_client.chat.completions.create.call_args[1]
    messages = call_args["messages"]
    assert len(messages) == 1
    assert (
            "指定された翻訳先の言語（Japanese）に翻訳してください。"
            in messages[0]["content"][0]["text"]
    )


@patch("translator.genai.Client")
def test_translator_gemini_call(mock_genai_client, dummy_pdf):
    # Setup mock
    mock_client_instance = MagicMock()
    mock_genai_client.return_value = mock_client_instance
    mock_response = MagicMock()
    mock_response.text = "This is a mock translation from Gemini."
    mock_client_instance.models.generate_content.return_value = mock_response

    # Initialize and translate
    translator = Translator(model_type="gemini-3-flash-preview", api_key="test_key")
    result = translator.translate_page(dummy_pdf, target_language="English")

    # Assertions
    assert result == "This is a mock translation from Gemini."
    mock_client_instance.models.generate_content.assert_called_once()

    # Check if prompt was passed correctly
    call_args = mock_client_instance.models.generate_content.call_args[1]
    assert call_args["model"] == "gemini-3-flash-preview"
    assert (
            "指定された翻訳先の言語（English）に翻訳してください。"
            in call_args["contents"][0]
    )


def test_translator_prompt_with_context():
    # Only test the internal get_prompt method to avoid making actual API calls
    translator = Translator(
        model_type="gpt-5.4-mini", api_key="dummy"
    )  # Need dummy key just to initialize

    context = "This is the end of the previous page."
    prompt = translator._get_prompt(
        target_language="Japanese", previous_context=context
    )

    assert (
            "前のページからの続きです。以下の文脈を考慮して翻訳してください：\nThis is the end of the previous page."
            in prompt
    )
