import pytest

from i18n import I18N


class Object:
    attr = "attr value"


@pytest.fixture
def i18n() -> I18N:
    _i18n = I18N("en", "tests/locales/")

    _i18n.register_function("func_call", lambda: "func result")
    _i18n.register_function("add", lambda x, y: x + y)

    _i18n.register_constant("CONST_VAR", "const var value")
    print(_i18n.loaded_translations)

    return _i18n


def test_load(i18n: I18N):
    assert i18n.loaded_translations == {
        "ru": {"hello-world": "привет мир"},
        "en": {
            "hello-world": "hello world",
            "hello-name": "hello {name}",
            "with-const": "text {const:CONST_VAR} text",
            "with-func": "text {func:func_call()} text",
            "with-obj": "text {obj:object.attr} text",
            "nested": {"key": "value"},
        },
    }


def test_t(i18n: I18N):
    assert i18n.t("en", "hello-world") == "hello world"
    assert i18n.t("en", "hello-name", name="Alex") == "hello Alex"
    assert i18n.t("en", "with-const") == "text const var value text"
    assert i18n.t("en", "with-func") == "text func result text"
    assert i18n.t("en", "with-obj", object=Object) == "text attr value text"
    assert i18n.t("en", "hello-name") == "hello [Error: `name` is not defined]"
    assert i18n.t("en", "nested.key") == "value"

    assert i18n.t("ru", "hello-world") == "привет мир"
    assert i18n.t("ru", "hello-name", name="Alex") == "hello Alex"


def test_available_locales(i18n: I18N):
    assert len(i18n.available_locales) == 2
    assert "en" in i18n.available_locales
    assert "ru" in i18n.available_locales
