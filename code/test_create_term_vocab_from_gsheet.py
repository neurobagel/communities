import pandas as pd
import pandera.pandas as pa
import pytest
from create_term_vocab_from_gsheet import vocab_file_schema


def test_invalid_term_ids_fail_validation():
    """Test that term IDs containing invalid characters fail schema validation."""
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
