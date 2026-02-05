import argparse
import json
import logging
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

gc = gspread.api_key(GOOGLE_API_KEY)


vocab_file_schema = pa.DataFrameSchema(
    # 'id', 'name', 'abbreviation', and 'description' are required columns,
    # but only 'id' and 'name' must not have any missing values
    {
        "id": pa.Column(
            str,
            checks=[
                pa.Check(
                    lambda id: id.is_unique, error="Term IDs must be unique."
                ),
                pa.Check.str_matches(
                    pattern=r"^[A-Za-z0-9_-]+$",
                    error="Term IDs must only contain alphanumeric characters, underscores, and hyphens.",
                ),
            ],
            nullable=False,
        ),
        "name": pa.Column(str, nullable=False),
        "abbreviation": pa.Column(str, nullable=True),
        "description": pa.Column(str, nullable=True),
        "same_as": pa.Column(str, nullable=True, required=False),
        "status": pa.Column(str, nullable=True, required=False),
        "invalid_reason": pa.Column(str, nullable=True, required=False),
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
        logger.error(f"Failed to access Google Sheet: {e.__cause__ or e}")
        sys.exit(1)
    vocab_worksheet = gsheet.get_worksheet(0)
    vocab_df = pd.DataFrame(
        vocab_worksheet.get_all_records(default_blank=None)
    )
    # Make column names case-insensitive
    vocab_df = vocab_df.rename(columns=str.lower)

    return vocab_df


def remove_rows_with_invalid_reason(vocab_table: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows from the vocabulary table that have a non-empty 'invalid_reason' field,
    i.e. terms that have been marked as invalid for some reason,
    and remove the 'invalid_reason' column from the resulting filtered table.
    """
    if "invalid_reason" not in vocab_table.columns:
        return vocab_table

    invalid_term_mask = vocab_table["invalid_reason"].notna() & (
        vocab_table["invalid_reason"].str.strip() != ""
    )
    if invalid_term_mask.any():
        invalid_rows = vocab_table.loc[
            invalid_term_mask, ["id", "name", "invalid_reason"]
        ]
        num_invalid_terms = len(invalid_rows)
        logger.info(f"{num_invalid_terms} invalid term(s) removed:")
        for _, row in invalid_rows.iterrows():
            logger.info(
                f"- id={row['id']}, name={row['name']}, invalid_reason={row['invalid_reason']}"
            )
    valid_term_rows = vocab_table[~invalid_term_mask].copy()
    return valid_term_rows.drop(columns="invalid_reason")


def create_terms_json(
    vocab_table: pd.DataFrame, vocab_metadata: dict
) -> list[dict]:
    """Create a standardized terms vocabulary dictionary from a vocabulary table."""
    valid_term_rows = remove_rows_with_invalid_reason(vocab_table)
    vocab_records = valid_term_rows.to_dict(orient="records")
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
        logger.error(
            f"Community directory does not exist: {args.community_config_dir}"
        )
        sys.exit(1)
    if not (
        args.community_config_dir / COMMUNITY_TERMS_MANIFEST_FILE
    ).is_file():
        logger.error(
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

        logger.info(
            f"Generating {output_filepath} from Google Sheet ID {vocab_gsheet_id}..."
        )

        vocab_df = fetch_gsheet_to_df(vocab_gsheet_id)

        try:
            vocab_df = vocab_file_schema.validate(vocab_df)
        except pa.errors.SchemaError as err:
            logger.error(f"The provided vocabulary table is invalid: {err}")
            sys.exit(1)

        terms_json = create_terms_json(vocab_df, vocab_metadata)

        with open(Path(output_filepath), "w") as f:
            json.dump(terms_json, f, indent=2)

        logger.info(f"Successfully generated {output_filepath}.")


if __name__ == "__main__":
    main()
