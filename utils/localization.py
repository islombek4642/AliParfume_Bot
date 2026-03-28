import json
import os
from typing import Any

class Localization:
    def __init__(self, default_lang: str = "uz"):
        self.default_lang = default_lang
        self.locales: dict[str, dict[str, str]] = {}
        self.load_locales()

    def load_locales(self):
        locales_path = "data/locales"
        for filename in os.listdir(locales_path):
            if filename.endswith(".json"):
                lang_code = filename.split(".")[0]
                with open(os.path.join(locales_path, filename), "r", encoding="utf-8") as f:
                    self.locales[lang_code] = json.load(f)

    def get(self, key: str, lang: str = "uz") -> str:
        # Fallback to default if lang not found
        lang_data = self.locales.get(lang, self.locales.get(self.default_lang, {}))
        return lang_data.get(key, key)

    def get_all(self, key: str) -> list[str]:
        """Returns the translation of a key in all loaded languages."""
        return [locale.get(key, key) for locale in self.locales.values()]

# Global instance
I18N = Localization()
_ = I18N.get
