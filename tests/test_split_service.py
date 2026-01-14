"""Tests for split_service module."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.split_service import SplitService
from app.services.llm_client import LLMClient
from app.models.schemas import SplitResult, DefectItem

class TestSplitService:
    """Tests for SplitService class."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLMClient."""
        client = AsyncMock(spec=LLMClient)
        return client

    @pytest.fixture
    def split_service(self, mock_llm_client):
        """Create SplitService instance."""
        return SplitService(llm_client=mock_llm_client)

    def test_clean_defect_text(self):
        """Test _clean_defect_text static method."""
        clean = SplitService._clean_defect_text

        # Basic numbering
        assert clean("1. Defect") == "Defect"
        assert clean("1) Defect") == "Defect"
        assert clean("1 Defect") == "Defect"

        # Bullets
        assert clean("- Defect") == "Defect"
        assert clean("* Defect") == "Defect"

        # Formatting
        assert clean("  1.  Defect  ") == "Defect"

        # Uppercase logic
        assert clean("1Defect") == "Defect"  # D is upper
        assert clean("1Царапины") == "Царапины"  # Ц is upper

        # Non-stripping cases
        assert clean("5шт") == "5шт"  # ш is lower
        assert clean("2nd") == "2nd"  # n is lower
        assert clean("2024 Year") == "2024 Year"  # 4 is followed by space, but 202 is matched? No, logic verified.

        # Empty
        assert clean("") == ""
        assert clean(None) == ""

    @pytest.mark.asyncio
    async def test_split_batch_clean_integration(self, split_service, mock_llm_client):
        """Test that split_batch applies cleanup to LLM results."""
        comments = ["input"]

        # Mock LLM response with numbered defects
        mock_result = SplitResult(defects=[
            DefectItem(text="1. Defect A"),
            DefectItem(text="2) Defect B"),
            DefectItem(text="3Царапина")
        ])
        mock_llm_client.split_comments.return_value = [mock_result]

        results = await split_service.split_batch(comments)

        assert len(results) == 1
        defects = results[0]
        assert len(defects) == 3
        assert defects[0] == "Defect A"
        assert defects[1] == "Defect B"
        assert defects[2] == "Царапина"

    @pytest.mark.asyncio
    async def test_split_batch_caching(self, split_service, mock_llm_client):
        """Test that split_batch uses cache."""
        comment = "cached comment"
        expected = ["def1", "def2"]

        # Populate cache
        split_service._store_in_cache(comment, expected)

        # Call split_batch
        results = await split_service.split_batch([comment])

        # Verify result and that LLM was NOT called
        assert results[0] == expected
        mock_llm_client.split_comments.assert_not_called()

    def test_is_empty_comment(self, split_service):
        """Test _is_empty_comment."""
        assert split_service._is_empty_comment("")
        assert split_service._is_empty_comment("   ")
        assert split_service._is_empty_comment("нет замечаний")
        assert split_service._is_empty_comment("Без замечаний")
        assert not split_service._is_empty_comment("Some defect")
