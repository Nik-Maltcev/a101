"""Tests for expand_service module."""

import pytest
from app.services.expand_service import expand_rows, expand_single_row, COMMENT_COLUMN_NAME
from app.models.schemas import ExpandedRow


class TestExpandRows:
    """Tests for expand_rows function."""
    
    def test_basic_expansion(self):
        """Test basic row expansion with multiple defects."""
        rows = [
            {"ID": "1", "NAME": "Item1", "КОММЕНТАРИЙ": "original comment"},
        ]
        defects = [["defect A", "defect B"]]
        
        result = expand_rows(rows, defects)
        
        assert len(result) == 2
        assert all(isinstance(r, ExpandedRow) for r in result)
    
    def test_row_expansion_count_req_4_1_4_4(self):
        """Requirement 4.1, 4.4: N defects creates N rows."""
        rows = [{"ID": "1", "КОММЕНТАРИЙ": "many defects"}]
        defects = [["d1", "d2", "d3", "d4", "d5"]]
        
        result = expand_rows(rows, defects)
        
        assert len(result) == 5
    
    def test_column_copy_req_4_2(self):
        """Requirement 4.2: All original columns are copied."""
        rows = [{"A": "1", "B": "2", "C": "3", "КОММЕНТАРИЙ": "test"}]
        defects = [["defect"]]
        
        result = expand_rows(rows, defects)
        
        assert result[0].original_data["A"] == "1"
        assert result[0].original_data["B"] == "2"
        assert result[0].original_data["C"] == "3"
    
    def test_comment_replaced_req_4_3(self):
        """Requirement 4.3: КОММЕНТАРИЙ column replaced with defect text."""
        rows = [{"ID": "1", "КОММЕНТАРИЙ": "original comment"}]
        defects = [["new defect text"]]
        
        result = expand_rows(rows, defects)
        
        assert result[0].original_data["КОММЕНТАРИЙ"] == "new defect text"
        assert result[0].defect_text == "new defect text"
    
    def test_multiple_rows_multiple_defects(self):
        """Test expansion with multiple rows having different defect counts."""
        rows = [
            {"ID": "1", "КОММЕНТАРИЙ": "comment1"},
            {"ID": "2", "КОММЕНТАРИЙ": "comment2"},
            {"ID": "3", "КОММЕНТАРИЙ": "comment3"},
        ]
        defects = [
            ["d1", "d2"],      # 2 defects
            ["d3"],           # 1 defect
            ["d4", "d5", "d6"],  # 3 defects
        ]
        
        result = expand_rows(rows, defects)
        
        assert len(result) == 6  # 2 + 1 + 3
        
        # Verify order and content
        assert result[0].original_data["ID"] == "1"
        assert result[0].defect_text == "d1"
        assert result[1].original_data["ID"] == "1"
        assert result[1].defect_text == "d2"
        assert result[2].original_data["ID"] == "2"
        assert result[2].defect_text == "d3"
    
    def test_empty_defects_skipped(self):
        """Rows with empty defect lists are skipped."""
        rows = [
            {"ID": "1", "КОММЕНТАРИЙ": "has defects"},
            {"ID": "2", "КОММЕНТАРИЙ": "no defects"},
        ]
        defects = [
            ["defect"],
            [],  # Empty - row should be skipped
        ]
        
        result = expand_rows(rows, defects)
        
        assert len(result) == 1
        assert result[0].original_data["ID"] == "1"
    
    def test_all_empty_defects(self):
        """All rows with empty defects returns empty list."""
        rows = [
            {"ID": "1", "КОММЕНТАРИЙ": "no issues"},
            {"ID": "2", "КОММЕНТАРИЙ": "no issues"},
        ]
        defects = [[], []]
        
        result = expand_rows(rows, defects)
        
        assert len(result) == 0
    
    def test_category_initially_none(self):
        """Category field should be None initially."""
        rows = [{"ID": "1", "КОММЕНТАРИЙ": "test"}]
        defects = [["defect"]]
        
        result = expand_rows(rows, defects)
        
        assert result[0].category is None
    
    def test_original_row_not_modified(self):
        """Original row dict should not be modified."""
        original_row = {"ID": "1", "КОММЕНТАРИЙ": "original"}
        rows = [original_row]
        defects = [["new defect"]]
        
        expand_rows(rows, defects)
        
        # Original should be unchanged
        assert original_row["КОММЕНТАРИЙ"] == "original"
    
    def test_mismatched_lengths_raises_error(self):
        """Mismatched rows and defects lengths should raise ValueError."""
        rows = [{"ID": "1", "КОММЕНТАРИЙ": "test"}]
        defects = [["d1"], ["d2"]]  # 2 defect lists for 1 row
        
        with pytest.raises(ValueError, match="Mismatch"):
            expand_rows(rows, defects)
    
    def test_empty_inputs(self):
        """Empty inputs return empty list."""
        assert expand_rows([], []) == []


class TestExpandSingleRow:
    """Tests for expand_single_row convenience function."""
    
    def test_single_row_expansion(self):
        """Test expanding a single row."""
        row = {"ID": "1", "КОММЕНТАРИЙ": "test"}
        defects = ["d1", "d2"]
        
        result = expand_single_row(row, defects)
        
        assert len(result) == 2
        assert result[0].defect_text == "d1"
        assert result[1].defect_text == "d2"
    
    def test_single_row_empty_defects(self):
        """Single row with no defects returns empty list."""
        row = {"ID": "1", "КОММЕНТАРИЙ": "test"}
        
        result = expand_single_row(row, [])
        
        assert len(result) == 0
