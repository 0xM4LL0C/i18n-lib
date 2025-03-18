import re
from pathlib import Path
from typing import Any, Callable, Optional

import yaml


class FallbackDict(dict[str, Any]):
    """A dictionary that returns a default error message for missing keys."""

    def __missing__(self, key: str) -> str:
        """Return a default error message for missing keys.

        Args:
            key (str): The missing key.

        Returns:
            str: The error message.
        """
        return f"[Error: key '{key}' is not defined]"


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
        self.functions: dict[str, Callable[..., Any]] = {}
        self.constants: dict[str, Any] = {}

        self.load()

    def load(self) -> None:
        """Load translations from locale files."""
        for locale in Path(self.load_path).iterdir():
            if locale.is_file() and locale.suffix in (".yaml", ".yml"):
                with locale.open(encoding="utf-8") as f:
                    self.loaded_translations[locale.stem] = yaml.safe_load(f) or {}

    def _get_nested_translation(self, data: dict[str, Any], key: str) -> Optional[dict[str, Any]]:
        """Retrieve a nested translation from the data dictionary.

        Args:
            data (dict): The dictionary containing translations.
            key (str): The key for the desired translation.

        Returns:
            Optional[dict[str, Any]]: The nested translation or None if not found.
        """
        keys = key.split(".")
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return None
        return data

    def register_function(self, name: str, func: Callable[..., Any]) -> None:
        """Register a custom function for use in translations.

        Args:
            name (str): The name of the function.
            func (Callable): The function to register.
        """
        self.functions[name] = func

    def register_constant(self, name: str, value: Any) -> None:
        """Register a constant for use in translations.

        Args:
            name (str): The name of the constant.
            value (Any): The value of the constant.
        """
        self.constants[name] = value

    def _eval_function(self, func_call: str, **kwargs: Any) -> str:
        """Evaluate a function call within a translation string.

        Args:
            func_call (str): The function call string.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The result of the function call or an error message if the function is not defined.
        """
        func_pattern = re.compile(r"(\w+)\((.*?)\)")
        match = func_pattern.match(func_call)
        if not match:
            return func_call

        func_name, args_str = match.groups()
        if func_name not in self.functions:
            return f"[Error: function '{func_name}' is not defined]"

        def replace_var(match: re.Match[str]) -> str:
            key = match.group(1)
            return str(kwargs.get(key, f"[Error: key '{key}' is not defined]"))

        args_str = re.sub(r"\{(\w+)\}", replace_var, args_str)

        args = []
        kwargs_func = {}

        if args_str:
            for arg in re.split(r",\s*(?![^()]*\))", args_str):
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    kwargs_func[key.strip()] = eval(value.strip(), {}, {})
                else:
                    args.append(eval(arg.strip(), {}, {}))

        return str(self.functions[func_name](*args, **kwargs_func))

    def _eval_constant(self, const_name: str) -> str:
        """Evaluate a constant within a translation string.

        Args:
            const_name (str): The name of the constant.

        Returns:
            str: The value of the constant or an error message if the constant is not defined.
        """
        if const_name in self.constants:
            return str(self.constants[const_name])
        return f"[Error: constant '{const_name}' is not defined]"

    def _eval_object_attr(self, obj: Any, attr_path: str) -> str:
        """Evaluate an object's attribute within a translation string.

        Args:
            obj (Any): The object containing the attribute.
            attr_path (str): The dot-separated path to the attribute.

        Returns:
            str: The value of the attribute or an error message if the attribute is not found.
        """
        try:
            attrs = attr_path.split(".")
            value = obj
            for attr in attrs:
                value = getattr(value, attr)
            return str(value)
        except AttributeError:
            return f"[Error: attribute '{attr_path}' not found in object]"

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
            func_pattern = re.compile(r"\{func:(.*?)\}")
            translation = func_pattern.sub(
                lambda m: self._eval_function(m.group(1), **kwargs), translation
            )

            const_pattern = re.compile(r"\{const:(.*?)\}")
            translation = const_pattern.sub(lambda m: self._eval_constant(m.group(1)), translation)

            obj_pattern = re.compile(r"\{obj\.(.*?)\}")
            if "obj" in kwargs:
                translation = obj_pattern.sub(
                    lambda m: self._eval_object_attr(kwargs["obj"], m.group(1)),
                    translation,
                )
            return translation.format_map(FallbackDict(kwargs))
        return key

    @property
    def available_locales(self) -> set[str]:
        """Get the set of available locales.

        Returns:
            set[str]: The set of available locales.
        """
        return set(self.loaded_translations.keys())
