import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path

import bidsschematools as bst
import bidsschematools.schema

logging.getLogger("bidsschematools").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

VOCAB_METADATA = {
    "namespace_prefix": "bids",
    "namespace_url": "https://bids.neuroimaging.io/terms/",
    "vocabulary_name": "BIDS imaging modalities",
    "version": "1.0.0",
}

# For reference
# INCLUDE_DATATYPES = ["anat", "dwi", "eeg", "emg", "func", "ieeg", "meg", "mrs", "nirs", "perf", "pet"]
EXCLUDE_DATATYPES = [
    "beh",
    "channels",
    "events",
    "fmap",
    "micr",
    "motion",
    "photo",
    "task",
]
DEPRECATION_TERMS = ["deprecated", "replaced", "**change:**"]

schema = bst.schema.load_schema()


def create_term_for_suffix(suffix: str, datatype: str) -> dict:
    suffix_info = schema.objects.suffixes[suffix].to_dict()
    return {
        "id": suffix,
        "name": suffix_info["display_name"],
        "abbreviation": suffix,  # TODO: Can consider removing since 'id' will now always have the same value
        "description": suffix_info["description"],
        "data_type": datatype,
    }


def get_terms_with_duplicate_labels(terms: dict) -> dict:
    terms_by_label = defaultdict(list)

    for term in terms.values():
        key = term["name"].lower()
        terms_by_label[key].append(term)

    return {
        label: terms
        for label, terms in terms_by_label.items()
        if len(terms) > 1
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate standardized terms vocabulary JSON file for BIDS-supported imaging modalities."
    )
    parser.add_argument(
        "community_config_dir",
        type=Path,
        help="Path to a community configuration directory.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    out_file = args.community_config_dir / "imaging_modalities.json"

    terms = defaultdict(list)
    for datatype, datatype_info in schema.rules.files.raw.items():
        if datatype in EXCLUDE_DATATYPES:
            continue

        for group in datatype_info.values():
            for suffix in group["suffixes"]:
                term = create_term_for_suffix(suffix, datatype)

                # Exclude suffixes that are marked as deprecated in their description, to help avoid terms with duplicate labels
                if any(
                    deprecation_term in term["description"].lower()
                    for deprecation_term in DEPRECATION_TERMS
                ):
                    logger.warning(f"Skipping deprecated suffix: {suffix}")
                # Some suffixes appear under multiple 'groups' within the same sub_datatype (e.g., suffix "meg")
                # and thus would have the same term metadata
                elif term not in terms[suffix]:
                    terms[suffix].append(term)

    single_datatype_terms = {}
    for suffix, instances in terms.items():
        if len(instances) > 1:
            logger.warning(
                f"Excluding suffix '{suffix}' - appears in multiple datatypes: {[instance['data_type'] for instance in instances]}."
            )
        else:
            single_datatype_terms[suffix] = instances[0]

    # Sanity check for any remaining terms with different suffixes but the same label
    duplicate_labels = get_terms_with_duplicate_labels(single_datatype_terms)
    if duplicate_labels:
        logger.warning(f"{len(duplicate_labels)} duplicated term labels found")
        logger.info(
            f"Duplicate labels:\n{json.dumps(duplicate_labels, indent=2)}"
        )

    vocab = [
        {
            **VOCAB_METADATA,
            "terms": list(terms.values()),
        }
    ]

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2)


if __name__ == "__main__":
    main()
