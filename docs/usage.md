# Usage

This documentation provides a detailed explanation of how to use the I18N class
for internationalization (i18n) in your Python projects. The I18N class allows
you to manage translations, constants, and functions, and dynamically inject
them into your translated strings.

## Initializing the I18N Instance

Create an instance of the I18N class by specifying the default locale and the
path where your translation files are located:

```python
from i18n import I18N

i18n = I18N(default_locale="en", load_path="locales/")
```

## Registering Constants

You can register constants that can be used in your translations.
Constants are static values that do not change during runtime.

```python
i18n.register_const("CONST_VAR", "some value")
```

## Registering Functions

You can also register functions that can be called dynamically within your translations.
Functions can take arguments and return values that are injected into the translated strings.

## Translating Strings

To translate a string, use the t method of the I18N instance. The t method takes
the locale, the translation key, and any additional keyword arguments that will
be used in the translation.

```python
print(i18n.t("en", "greet", name="Jake"))  # Output: "hello Jake"
print(i18n.t("en", "with-const"))  # Output: "with const: some value"
print(i18n.t("en", "with-func"))  # Output: "with func call: Alex"
print(i18n.t("en", "func-with-args"))  # Output: "func call with args: 2"
print(i18n.t("en", "with-obj", object=SomeObject))  # Output: "with object attribute: some value"
```

## Translation File Structure

```yaml
greet: hello {name}
with-const: "with const: {const:CONST_VAR}"
with-func: "with func call: {func:get_name()}"
func-with-args: "func call with args: {func:add(1, 1)}"
with-obj: "with object attribute: {obj:object.some_attribute}"
```

## Fallback to Default Locale

If a translation key is not found in the specified locale, the I18N class will
fall back to the default locale:

```python
print(i18n.t("fr", "greet", name="Jake"))  # Output: "hello Jake" (fallback to "en" locale)
```

## Handling Missing Keys

If a translation key is missing in both the specified locale and the default
locale, the t method will return the key itself:

```python
print(i18n.t("en", "missing_key"))  # Output: "missing_key"
```
