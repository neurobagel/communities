import pandas as pd
import pandera.pandas as pa
import pytest
from create_term_vocab_from_gsheet import vocab_file_schema


def test_invalid_term_ids_fail_validation():
    """
    Test that term IDs containing invalid characters fail schema validation.
    """
    invalid_vocab_table = pd.DataFrame(
        {
            "id": ["TERM-1", "TERM_2", "TERM2!", "TERM 3"],
            "name": [
                "Valid Term 1",
                "Valid Term 2",
                "Invalid Term 3",
                "Invalid Term 4",
            ],
            "abbreviation": ["T1", "T2", "T3", "T4"],
            "description": [
                "Term 1 description",
                "Term 2 description",
                "Term 3 description",
                "Term 4 description",
            ],
        }
    )
    expected_error = "must only contain alphanumeric characters"
    valid_ids = ["TERM-1", "TERM_2"]
    invalid_ids = ["TERM2!", "TERM 3"]

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        vocab_file_schema.validate(invalid_vocab_table)

    assert expected_error in str(exc_info.value)
    for valid_id in valid_ids:
        assert valid_id not in str(exc_info.value)
    for invalid_id in invalid_ids:
        assert invalid_id in str(exc_info.value)


@pytest.mark.parametrize(
    "all_none_column",
    ["abbreviation", "description", "same_as", "status", "invalid_reason"],
)
def test_column_all_none_passes_validation(all_none_column):
    """
    Regression: any nullable column that is entirely
    None should pass schema validation.
    """
    vocab_table = pd.DataFrame(
        {
            "id": ["TERM-1", "TERM-2"],
            "name": ["Term 1", "Term 2"],
            "abbreviation": ["T1", "T2"],
            "description": ["Term 1 description", "Term 2 description"],
            "same_as": ["snomed:1234", "snomed:5678"],
            "status": ["active", "active"],
            "invalid_reason": ["", ""],
        }
    )
    vocab_table[all_none_column] = None
    validated = vocab_file_schema.validate(vocab_table)
    assert list(validated["id"]) == ["TERM-1", "TERM-2"]


@pytest.mark.parametrize(
    "column_with_one_none",
    ["abbreviation", "description", "same_as", "status", "invalid_reason"],
)
def test_column_one_none_passes_validation(column_with_one_none):
    """
    Any nullable column with a single None
    value (among other values) should pass schema validation.
    """
    vocab_table = pd.DataFrame(
        {
            "id": ["TERM-1", "TERM-2"],
            "name": ["Term 1", "Term 2"],
            "abbreviation": ["T1", "T2"],
            "description": ["Term 1 description", "Term 2 description"],
            "same_as": ["snomed:1234", "snomed:5678"],
            "status": ["active", "active"],
            "invalid_reason": ["", ""],
        }
    )
    vocab_table.loc[0, column_with_one_none] = None
    validated = vocab_file_schema.validate(vocab_table)
    assert list(validated["id"]) == ["TERM-1", "TERM-2"]
