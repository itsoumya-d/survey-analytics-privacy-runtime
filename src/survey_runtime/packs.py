import json
from pathlib import Path
from typing import Any, Dict, List

SUPPORTED_COUNTRIES = {
    "base": "base",
    "default": "base",
    "ie": "ie",
    "ireland": "ie"
}


def get_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    while curr.parent != curr:
        if (curr / "packs").exists() or (curr / "pyproject.toml").exists():
            return curr
        curr = curr.parent
    return Path.cwd()


def load_country_pack(country: str = "base") -> List[Dict[str, Any]]:
    """Loads declarative compliance rules for a specified jurisdiction."""
    normalized = (country or "base").strip().lower()
    matched = SUPPORTED_COUNTRIES.get(normalized)
    if not matched:
        raise ValueError(f"Unknown country code: '{country}'. Supported: base, ie")

    root = get_project_root()
    pack_path = root / "packs" / matched / "rules.json"
    if not pack_path.exists():
        raise FileNotFoundError(f"Country pack rules missing at: {pack_path}")

    with open(pack_path, "r", encoding="utf-8") as f:
        return json.load(f)
