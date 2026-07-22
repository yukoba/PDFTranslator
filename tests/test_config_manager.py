import json
from unittest.mock import patch

import pytest

from config_manager import ConfigManager, APP_NAME


@pytest.fixture
def mock_config_dir(tmp_path):
    """Fixture to provide a temporary directory for config testing."""
    with patch("config_manager.ConfigManager._get_config_dir", return_value=tmp_path):
        yield tmp_path


def test_config_initialization_defaults(mock_config_dir):
    config = ConfigManager()
    assert config.get("target_language") == "Japanese"
    assert config.get("selected_model") == "gemini-flash-latest"
    assert config.get("last_opened_folder") == ""
    assert mock_config_dir.exists()
    assert (mock_config_dir / "config.json").exists() == False  # Only saved when changed


def test_config_set_and_save(mock_config_dir):
    config = ConfigManager()
    config.set("selected_model", "gemini-flash-latest")

    assert config.get("selected_model") == "gemini-flash-latest"

    # Check if it was saved to file
    config_file = mock_config_dir / "config.json"
    assert config_file.exists()

    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["selected_model"] == "gemini-flash-latest"


def test_config_load_existing(mock_config_dir):
    # Pre-create a config file
    config_file = mock_config_dir / "config.json"
    mock_config_dir.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump({"last_opened_folder": "/path/to/my/docs"}, f)

    config = ConfigManager()
    assert config.get("last_opened_folder") == "/path/to/my/docs"
    # Defaults should still be present for missing keys
    assert config.get("target_language") == "Japanese"


@patch("config_manager.keyring.get_password")
def test_get_api_key(mock_get_password, mock_config_dir):
    mock_get_password.return_value = "my_secret_key"
    config = ConfigManager()
    key = config.get_api_key("gpt-5.6-luna")

    assert key == "my_secret_key"
    mock_get_password.assert_called_once_with(APP_NAME, "OpenAI")


@patch("config_manager.keyring.set_password")
def test_set_api_key(mock_set_password, mock_config_dir):
    config = ConfigManager()
    config.set_api_key("gemini-flash-latest", "new_secret_key")

    mock_set_password.assert_called_once_with(APP_NAME, "Gemini", "new_secret_key")
