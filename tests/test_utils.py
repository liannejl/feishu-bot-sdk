"""Tests for feishu_sdk.utils module."""

import pytest

from feishu_sdk.utils import Obj, dict_2_obj


class TestObj:
    """Tests for the Obj class."""

    def test_simple_dict(self):
        """Test converting a simple flat dictionary."""
        data = {"name": "test", "value": 123}
        obj = Obj(data)
        assert obj.name == "test"
        assert obj.value == 123

    def test_nested_dict(self):
        """Test converting nested dictionaries."""
        data = {"user": {"name": "John", "email": "john@example.com"}}
        obj = Obj(data)
        assert obj.user.name == "John"
        assert obj.user.email == "john@example.com"

    def test_list_of_dicts(self):
        """Test converting lists containing dictionaries."""
        data = {"items": [{"id": 1, "name": "first"}, {"id": 2, "name": "second"}]}
        obj = Obj(data)
        assert len(obj.items) == 2
        assert obj.items[0].id == 1
        assert obj.items[0].name == "first"
        assert obj.items[1].id == 2
        assert obj.items[1].name == "second"

    def test_list_of_primitives(self):
        """Test lists with primitive values."""
        data = {"tags": ["a", "b", "c"]}
        obj = Obj(data)
        assert obj.tags == ["a", "b", "c"]

    def test_mixed_list(self):
        """Test lists with mixed types."""
        data = {"mixed": [{"key": "value"}, "string", 123]}
        obj = Obj(data)
        assert obj.mixed[0].key == "value"
        assert obj.mixed[1] == "string"
        assert obj.mixed[2] == 123

    def test_tuple_handling(self):
        """Test that tuples are also handled."""
        data = {"coords": ({"x": 1}, {"y": 2})}
        obj = Obj(data)
        assert obj.coords[0].x == 1
        assert obj.coords[1].y == 2

    def test_empty_dict(self):
        """Test converting an empty dictionary."""
        obj = Obj({})
        # Should not raise an error
        assert isinstance(obj, Obj)


class TestDict2Obj:
    """Tests for the dict_2_obj function."""

    def test_basic_conversion(self):
        """Test basic dictionary to object conversion."""
        data = {"key": "value"}
        obj = dict_2_obj(data)
        assert isinstance(obj, Obj)
        assert obj.key == "value"

    def test_deeply_nested(self):
        """Test deeply nested structures."""
        data = {"level1": {"level2": {"level3": {"value": "deep"}}}}
        obj = dict_2_obj(data)
        assert obj.level1.level2.level3.value == "deep"
