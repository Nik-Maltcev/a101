"""Tests for LLMClient."""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.llm_client import LLMClient, _extract_json_from_text, _fix_json_string

class TestLLMClientUtils:
    """Tests for utility functions."""

    def test_extract_json(self):
        """Test extracting JSON from various text formats."""
        # Clean JSON
        assert _extract_json_from_text('{"a": 1}') == '{"a": 1}'

        # Markdown block
        assert _extract_json_from_text('Here is json:\n```json\n{"a": 1}\n```') == '{"a": 1}'

        # Text before JSON
        assert _extract_json_from_text('Reasoning...\n{"results": []}') == '{"results": []}'

        # Text before and after
        assert _extract_json_from_text('Start\n{"a": 1}\nEnd') == '{"a": 1}'

    def test_fix_json(self):
        """Test fixing common JSON errors."""
        # Trailing comma
        assert _fix_json_string('{"a": 1,}') == '{"a": 1}'
        assert _fix_json_string('[1, 2,]') == '[1, 2]'


class TestLLMClientParsing:
    """Tests for parsing LLM responses."""

    @pytest.fixture
    def client(self):
        """Create LLMClient instance."""
        return LLMClient(api_key="test")

    def test_parse_split_response_new_format(self, client):
        """Test parsing the new list of lists format."""
        response = json.dumps({
            "results": [
                ["defect 1", "defect 2"],
                ["defect 3"],
                []
            ]
        })

        results = client._parse_split_response(response, expected_count=3)

        assert len(results) == 3

        # Check first result
        assert len(results[0].defects) == 2
        assert results[0].defects[0].text == "defect 1"
        assert results[0].defects[1].text == "defect 2"

        # Check second result
        assert len(results[1].defects) == 1
        assert results[1].defects[0].text == "defect 3"

        # Check third result
        assert len(results[2].defects) == 0

    def test_parse_split_response_handles_padding(self, client):
        """Test padding results if LLM returns too few."""
        response = json.dumps({
            "results": [
                ["defect 1"]
            ]
        })

        results = client._parse_split_response(response, expected_count=2)

        assert len(results) == 2
        assert len(results[0].defects) == 1
        assert len(results[1].defects) == 0  # Padding

    def test_parse_split_response_handles_malformed_list(self, client):
        """Test handling cases where inner item is not a list."""
        response = json.dumps({
            "results": [
                "not a list",
                ["ok"]
            ]
        })

        results = client._parse_split_response(response, expected_count=2)

        assert len(results[0].defects) == 1
        assert results[0].defects[0].text == "not a list"  # Should be wrapped

        assert len(results[1].defects) == 1
        assert results[1].defects[0].text == "ok"
