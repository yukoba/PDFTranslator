import json
import os
import keyring
from pathlib import Path
from typing import Dict, Any, Optional

APP_NAME = "PDFTranslator"
CONFIG_FILE_NAME = "config.json"


class ConfigManager:
    def __init__(self):
        # Determine the path for the config file.
        # On Windows, this typically resolves to %APPDATA%\PDFTranslator
        # On Linux/macOS, it uses the standard config directories.
        self.config_dir = self._get_config_dir()
        self.config_path = self.config_dir / CONFIG_FILE_NAME
        self._ensure_config_dir_exists()

        self.config = self._load_config()

    def _get_config_dir(self) -> Path:
        if os.name == "nt":
            base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            base_dir = os.path.join(os.path.expanduser("~"), ".config")

        return Path(base_dir) / APP_NAME

    def _ensure_config_dir_exists(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        default_config = {
            "last_opened_folder": "",
            "source_language": "English",
            "target_language": "Japanese",
            "selected_model": "gpt-5-mini",
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # Update default config with loaded values
                    default_config.update(loaded_config)
            except (json.JSONDecodeError, IOError):
                # If the file is corrupted, return the default config
                pass

        return default_config

    def save_config(self):
        """Saves the current configuration to the JSON file."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save_config()

    # --- Secure API Key Management ---

    def get_api_key(self, model_name: str) -> Optional[str]:
        """Retrieves the API key securely from the OS keyring."""
        try:
            return keyring.get_password(APP_NAME, model_name)
        except Exception:
            # Handle keyring backend errors gracefully
            return None

    def set_api_key(self, model_name: str, api_key: str):
        """Saves the API key securely using the OS keyring."""
        try:
            keyring.set_password(APP_NAME, model_name, api_key)
        except Exception as e:
            print(f"Warning: Failed to save API key securely: {e}")

    def delete_api_key(self, model_name: str):
        """Deletes the API key from the OS keyring."""
        try:
            keyring.delete_password(APP_NAME, model_name)
        except Exception:
            pass  # Ignore if it doesn't exist
