from pathlib import Path
from typing import Any, Callable, Optional

import yaml

from i18n.formatter import StringFormatter

__all__ = ("I18N",)


class I18N:
    """Internationalization class for managing translations."""

    def __init__(
        self,
        default_locale: str,
        load_path: str = "locales/",
    ) -> None:
        """Initialize the I18N class.

        Args:
            default_locale (str): The default locale to use.
            load_path (str, optional): The path to the directory containing locale files. Defaults to "locales/".
        """
        self.load_path = load_path
        self.default_locale = default_locale
        self.loaded_translations: dict[str, dict[str, Any]] = {}
        self.context: dict[str, Any] = {}
        self.formatter = StringFormatter(self.context)

        self.load()

    def load(self) -> None:
        """Load translations from locale files."""
        if not Path(self.load_path).exists():
            self.loaded_translations = {}
            return

        for locale in Path(self.load_path).iterdir():
            if locale.is_file() and locale.suffix in (".yaml", ".yml"):
                with locale.open(encoding="utf-8") as f:
                    self.loaded_translations[locale.stem] = yaml.safe_load(f) or {}

    def _get_nested_translation(self, data: dict[str, Any], key: str) -> Optional[str]:
        """Retrieve a nested translation from the data dictionary.

        Args:
            data (dict): The dictionary containing translations.
            key (str): The key for the desired translation.

        Returns:
            Optional[str]: The nested translation or None if not found.
        """
        keys = key.split(".")
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return None
        return data if isinstance(data, str) else None

    def register_function(self, name: str, func: Callable[..., Any]) -> None:
        """Register a custom function for use in translations.

        Args:
            name (str): The name of the function.
            func (Callable): The function to register.
        """
        self.context[name] = func

    def register_constant(self, name: str, value: Any) -> None:
        """Register a constant for use in translations.

        Args:
            name (str): The name of the constant.
            value (Any): The value of the constant.
        """
        self.context[name] = value

    def t(self, locale: str, key: str, **kwargs: Any) -> str:
        """Translate a key for a given locale.

        Args:
            locale (str): The locale to use for translation.
            key (str): The key to translate.
            **kwargs: Additional keyword arguments for formatting the translation.

        Returns:
            str: The translated string or the key if no translation is found.
        """
        translation = (
            self._get_nested_translation(self.loaded_translations.get(locale, {}), key)
            or self._get_nested_translation(
                self.loaded_translations.get(self.default_locale, {}), key
            )
            or key
        )

        if isinstance(translation, str):
            return self.formatter.format(translation, **kwargs)

        return key

    @property
    def available_locales(self) -> set[str]:
        """Get the set of available locales.

        Returns:
            set[str]: The set of available locales.
        """
        return set(self.loaded_translations.keys())
