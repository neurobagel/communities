import gspread
import pandas as pd
import pandera.pandas as pa
import sys
import json
from pathlib import Path
import os

GOOGLE_API_KEY = os.environ.get("COMMUNITIES_GOOGLE_API_KEY")
VOCAB_GSHEET_ID = os.environ.get("ENIGMA_ASSESSMENTS_GSHEET_ID")
OUTPUT_FILEPATH = Path(__file__).absolute().parents[1] / "configs/ENIGMA-PD/assessment.json"

# TODO: Do we want to increment the version each time the config file is regenerated?
VOCAB_METADATA = {
    "namespace_prefix": "enigmapd",
    "namespace_url": "https://enigma.ini.usc.edu/ongoing/enigma-parkinsons/vocab/assessments/",
    "vocabulary_name": "ENIGMA-PD vocabulary of assessment terms",
    "version": "1.0.0"
}

gc = gspread.api_key(GOOGLE_API_KEY)


vocab_file_schema = pa.DataFrameSchema(
    # 'id', 'name', 'abbreviation', and 'description' are required columns,
    # but only 'id' and 'name' must not have any missing values
    {
        "id": pa.Column(str, checks=pa.Check.str_startswith("trm_"), nullable=False),
        "name": pa.Column(str, nullable=False),
        "abbreviation": pa.Column(str, nullable=True),
        "description": pa.Column(str, nullable=True),
        "same_as": pa.Column(str, nullable=True, required=False),
        "status": pa.Column(str, nullable=True, required=False)
    },
    # Only validate and pass to the result the columns defined in the schema
    strict="filter"
)


def fetch_gsheet(gsheet_id: str):
    """Access and open a public Google spreadsheet by its ID (found in the spreadsheet URL after /d/)."""
    try:
        gsheet = gc.open_by_key(gsheet_id)
    except (PermissionError, gspread.exceptions.APIError) as e:
        # gspread may wrap the original APIError in a PermissionError,
        # so we want to print the original cause if present
        print("Failed to access Google Sheet:", e.__cause__ or e)
        sys.exit(1)
    vocab_worksheet = gsheet.get_worksheet(0)
    return vocab_worksheet


def decapitalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Convert all column names in the DataFrame to lowercase."""
    df.columns = [col.lower() for col in df.columns]
    return df


def create_terms_json(vocab_table: pd.DataFrame, vocab_metadata: dict) -> list[dict]:
    vocab_records = vocab_table.to_dict(orient="records")
    return [{**vocab_metadata, "terms": vocab_records}]


def main():
    vocab_gsheet = fetch_gsheet(VOCAB_GSHEET_ID)
    vocab_df = pd.DataFrame(vocab_gsheet.get_all_records(default_blank=None))

    # Make column names case-insensitive
    vocab_df = decapitalize_column_names(vocab_df)

    try:
        vocab_df = vocab_file_schema.validate(vocab_df)
    except pa.errors.SchemaError as err:
        print("The provided vocabulary table is invalid:", err)
        sys.exit(1)

    terms_json = create_terms_json(vocab_df, VOCAB_METADATA)

    with open(Path(OUTPUT_FILEPATH), "w") as f:
        json.dump(terms_json, f, indent=2)


if __name__ == "__main__":
    main()
