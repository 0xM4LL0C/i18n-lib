import re
from collections import ChainMap
from typing import Any, Callable, Optional

__all__ = ("StringFormatter",)


class StringFormatter:
    def __init__(self, global_context: dict[str, Any]) -> None:
        """Initializes the StringFormatter with a global context.

        Args:
            global_context (dict[str, Any]): A dictionary containing global context variables.
        """
        self.global_context = global_context
        self.pattern = re.compile(r"\{([^{}]+)\}")

    def _resolve_expr(self, expr: str, **kwargs: Any) -> str:
        """Resolves an expression based on the context.

        Args:
            expr (str): The expression to resolve.
            **kwargs: Additional context variables.

        Returns:
            str: The resolved expression or an error message if the expression cannot be resolved.
        """
        ctx = ChainMap(kwargs, self.global_context)

        if expr.startswith("func:"):
            return self._call_function(expr[5:], **kwargs)
        if expr.startswith("obj:"):
            return self._get_object_attr(expr[4:], **kwargs)
        if expr.startswith("const:"):
            return ctx.get(expr[6:], f"[Error: const `{expr[6:]}` not defined]")
        return ctx.get(expr, f"[Error: `{expr}` is not defined]")

    def _call_function(self, expr: str, **kwargs: Any) -> str:
        """Calls a function based on the expression.

        Args:
            expr (str): The function expression to call.
            **kwargs: Additional context variables.

        Returns:
            str: The result of the function call or an error message if the function cannot be called.
        """
        ctx = ChainMap(kwargs, self.global_context)

        match = re.fullmatch(r"(\w+)\((.*)\)", expr)
        if not match:
            return f"[Error: Expression '{expr}' does not match the expected pattern]"

        func_name, func_args = match.groups()

        func: Optional[Callable[..., Any]] = ctx.get(func_name)

        if not func:
            return f"[Error: func `{func_name}` is not defined]"
        if not callable(func):
            return f"[Error: `{func_name}` is not callable]"
        return str(eval(f"{func_name}({func_args})", dict(ctx), {}))

    def _get_object_attr(self, expr: str, **kwargs: Any) -> str:
        """Gets an object's attribute based on the expression.

        Args:
            expr (str): The object attribute expression to resolve.
            **kwargs: Additional context variables.

        Returns:
            str: The value of the object's attribute or an error message if the attribute cannot be resolved.
        """
        ctx = ChainMap(kwargs, self.global_context)
        parts = expr.split(".")
        obj_name = parts[0]

        obj = ctx.get(obj_name)

        if obj is None:
            return f"[Error: object `{obj_name}` is not defined]"

        return str(eval(expr, dict(ctx), {}))

    def format(self, text: str, **kwargs: Any) -> str:
        """Formats a string by replacing placeholders with context values.

        Args:
            text (str): The text containing placeholders to format.
            **kwargs: Additional context variables.

        Returns:
            str: The formatted string with placeholders replaced by context values.
        """

        def replace(match: re.Match[str]) -> str:
            return str(self._resolve_expr(match.group(1), **kwargs))

        return self.pattern.sub(replace, text)
