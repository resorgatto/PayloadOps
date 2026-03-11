"""
PayloadOps — Unit Tests: Template Renderer

Tests for the payload variable injection engine.
"""

from __future__ import annotations

from apps.engine.renderer import render_template, resolve_variable


class TestResolveVariable:
    def test_simple_path(self):
        assert resolve_variable("name", {"name": "John"}) == "John"

    def test_nested_path(self):
        ctx = {"payload": {"user": {"name": "John"}}}
        assert resolve_variable("payload.user.name", ctx) == "John"

    def test_missing_path(self):
        assert resolve_variable("payload.missing", {"payload": {}}) is None

    def test_deeply_nested(self):
        ctx = {"a": {"b": {"c": {"d": "deep"}}}}
        assert resolve_variable("a.b.c.d", ctx) == "deep"


class TestRenderTemplate:
    def test_string_interpolation(self):
        result = render_template("Hello {{payload.name}}", {"payload": {"name": "World"}})
        assert result == "Hello World"

    def test_dict_template(self):
        template = {"text": "Hello {{payload.name}}", "channel": "#general"}
        context = {"payload": {"name": "John"}}
        result = render_template(template, context)
        assert result == {"text": "Hello John", "channel": "#general"}

    def test_preserve_type_for_single_variable(self):
        template = "{{payload.count}}"
        context = {"payload": {"count": 42}}
        result = render_template(template, context)
        assert result == 42
        assert isinstance(result, int)

    def test_nested_dict(self):
        template = {"data": {"name": "{{payload.name}}", "items": ["{{payload.item1}}"]}}
        context = {"payload": {"name": "Test", "item1": "A"}}
        result = render_template(template, context)
        assert result == {"data": {"name": "Test", "items": ["A"]}}

    def test_missing_variable_preserved(self):
        result = render_template("Hello {{payload.missing}}", {"payload": {}})
        assert result == "Hello {{payload.missing}}"

    def test_non_string_passthrough(self):
        assert render_template(42, {}) == 42
        assert render_template(None, {}) is None
        assert render_template(True, {}) is True
