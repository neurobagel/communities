import pandas as pd
import pandera.pandas as pa
import pytest
from create_term_vocab_from_gsheet import vocab_file_schema


def test_invalid_term_ids_fail_validation():
    """Test that term IDs containing invalid characters fail schema validation."""
    invalid_vocab_table = {
        "id": ["TERM1", "TERM2!", "TERM 3"],
        "name": ["Term 1", "Term 2", "Term 3"],
        "abbreviation": ["T1", "T2", "T3"],
        "description": [
            "Term 1 description",
            "Term 2 description",
            "Term 3 description",
        ],
    }
    expected_error_substrs = [
        "must only contain alphanumeric characters, underscores, and hyphens",
        "TERM2!",
        "TERM 3",
    ]

    df = pd.DataFrame(invalid_vocab_table)

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        vocab_file_schema.validate(df)

    for substr in expected_error_substrs:
        assert substr in str(exc_info.value)
