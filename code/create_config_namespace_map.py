"""
Create a file that maps each community configuration to the unique namespaces (prefixes and URLs)
it uses across standardized variable configuration and standardized term vocabulary files.
"""

import json
from pathlib import Path
from typing import Any

ALL_CONFIGS_DIR = Path(__file__).absolute().parents[1] / "configs"
CONFIG_METADATA_DIR = Path(__file__).absolute().parents[1] / "config_metadata"
OUTPUT_FILE = CONFIG_METADATA_DIR / "config_namespace_map.json"

FILE_TO_SKIP = "community_terms_manifest.json"


def load_json_config_file(filename: Path) -> Any:
    """Load a configuration JSON file."""
    with open(filename, encoding="utf-8") as f:
        return json.load(f)


def collect_namespaces_from_file(config: list[dict]) -> list[dict]:
    """Return a list of unique namespace prefix-url pairs used in a given configuration file."""
    all_namespaces_info = []

    for namespace in config:
        namespace_info = {
            key: namespace[key]
            for key in ["namespace_prefix", "namespace_url"]
        }
        if namespace_info not in all_namespaces_info:
            all_namespaces_info.append(namespace_info)

    return all_namespaces_info


def get_namespaces_for_config(config_dir: Path) -> dict:
    """
    For a given subcommunity configuration, return a dictionary containing all unique used namespaces
    for the configuration's standardized variables and terms.

    NOTE: We add hardcoded namespaces for imaging terms, as these are not configurable but are required
    vocabularies for processing imaging data.
    """
    imaging_term_namespaces = [
        {
            "namespace_prefix": "nidm",
            "namespace_url": "http://purl.org/nidash/nidm#",
        },
        {
            "namespace_prefix": "np",
            "namespace_url": "https://github.com/nipoppy/pipeline-catalog/tree/main/processing/",
        },
    ]

    config_namespaces = {}
    all_term_namespaces = []
    for json_file in config_dir.glob("*.json"):
        config_data = load_json_config_file(json_file)
        if json_file.name == "config.json":
            config_namespaces["variables"] = collect_namespaces_from_file(
                config_data
            )
        elif json_file.name != FILE_TO_SKIP:
            term_namespaces_for_variable = collect_namespaces_from_file(
                config_data
            )
            for namespace in term_namespaces_for_variable:
                if namespace not in all_term_namespaces:
                    all_term_namespaces.append(namespace)

    for ns in imaging_term_namespaces:
        if ns not in all_term_namespaces:
            all_term_namespaces.append(ns)

    config_namespaces["terms"] = all_term_namespaces
    result = {"config_name": config_dir.name, "namespaces": config_namespaces}
    return result


def main():
    config_namespace_map = []
    for config_dir in ALL_CONFIGS_DIR.iterdir():
        if config_dir.is_dir():
            config_namespaces = get_namespaces_for_config(config_dir)
            config_namespace_map.append(config_namespaces)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(config_namespace_map, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
