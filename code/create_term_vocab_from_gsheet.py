import argparse
import json
import os
import sys
from pathlib import Path

import gspread
import pandas as pd
import pandera.pandas as pa

GOOGLE_API_KEY = os.environ.get("COMMUNITIES_GOOGLE_API_KEY")
COMMUNITY_TERMS_MANIFEST_FILE = "community_terms_manifest.json"
VOCAB_METADATA_KEYS = [
    "namespace_prefix",
    "namespace_url",
    "vocabulary_name",
    "version",
]

gc = gspread.api_key(GOOGLE_API_KEY)


vocab_file_schema = pa.DataFrameSchema(
    # 'id', 'name', 'abbreviation', and 'description' are required columns,
    # but only 'id' and 'name' must not have any missing values
    {
        "id": pa.Column(
            str,
            checks=pa.Check(
                lambda id: id.is_unique, error="Term IDs must be unique."
            ),
            nullable=False,
        ),
        "name": pa.Column(str, nullable=False),
        "abbreviation": pa.Column(str, nullable=True),
        "description": pa.Column(str, nullable=True),
        "same_as": pa.Column(str, nullable=True, required=False),
        "status": pa.Column(str, nullable=True, required=False),
    },
    # Only validate and pass to the result the columns defined in the schema
    strict="filter",
)


def load_community_terms_manifest(community_config_dir: Path) -> dict:
    """Load the community terms manifest JSON file."""
    with open(community_config_dir / COMMUNITY_TERMS_MANIFEST_FILE) as f:
        return json.load(f)


def fetch_gsheet_to_df(gsheet_id: str) -> pd.DataFrame:
    """Access and open a public Google spreadsheet by its ID (found in the spreadsheet URL after /d/)."""
    try:
        gsheet = gc.open_by_key(gsheet_id)
    except (PermissionError, gspread.exceptions.APIError) as e:
        # gspread may wrap the original APIError in a PermissionError,
        # so we want to print the original cause if present
        print("Failed to access Google Sheet:", e.__cause__ or e)
        sys.exit(1)
    vocab_worksheet = gsheet.get_worksheet(0)
    vocab_df = pd.DataFrame(
        vocab_worksheet.get_all_records(default_blank=None)
    )
    # Make column names case-insensitive
    vocab_df = vocab_df.rename(columns=str.lower)

    return vocab_df


def create_terms_json(
    vocab_table: pd.DataFrame, vocab_metadata: dict
) -> list[dict]:
    vocab_records = vocab_table.to_dict(orient="records")
    return [{**vocab_metadata, "terms": vocab_records}]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate standardized terms vocabulary JSON files from Google Sheets tables for a Neurobagel community configuration."
    )
    parser.add_argument(
        "community_config_dir",
        type=Path,
        help="Path to a community configuration directory.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.community_config_dir.is_dir():
        print(
            f"Community directory does not exist: {args.community_config_dir}"
        )
        sys.exit(1)
    if not (
        args.community_config_dir / COMMUNITY_TERMS_MANIFEST_FILE
    ).is_file():
        print(
            f"{COMMUNITY_TERMS_MANIFEST_FILE} not found in {args.community_config_dir}"
        )
        sys.exit(1)

    community_terms_manifest = load_community_terms_manifest(
        args.community_config_dir
    )

    for std_trm_vocab_file, vocab_metadata in community_terms_manifest.items():
        vocab_gsheet_id = vocab_metadata.get("source_spreadsheet_id")
        output_filepath = args.community_config_dir / std_trm_vocab_file
        vocab_metadata = {
            key: vocab_metadata.get(key) for key in VOCAB_METADATA_KEYS
        }

        print(
            f"Generating {output_filepath} from Google Sheet ID {vocab_gsheet_id}..."
        )

        vocab_df = fetch_gsheet_to_df(vocab_gsheet_id)

        try:
            vocab_df = vocab_file_schema.validate(vocab_df)
        except pa.errors.SchemaError as err:
            print("The provided vocabulary table is invalid: ", err)
            sys.exit(1)

        terms_json = create_terms_json(vocab_df, vocab_metadata)

        with open(Path(output_filepath), "w") as f:
            json.dump(terms_json, f, indent=2)

        print(f"Successfully generated {output_filepath}.")


if __name__ == "__main__":
    main()
