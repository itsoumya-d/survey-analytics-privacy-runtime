import json
from pathlib import Path
from typing import Dict, Any, Optional

PACKS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "packs"

def load_country_pack(country: str, base_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Loads and validates rule definitions for a specific country pack."""
    if not country or not isinstance(country, str):
        raise ValueError("Country code must be a non-empty string.")
    
    code = country.strip().lower()
    search_dir = base_dir if base_dir is not None else PACKS_DIR
    pack_path = search_dir / code / "rules.json"
    
    if not pack_path.exists():
        available = [p.name for p in search_dir.iterdir() if p.is_dir()] if search_dir.exists() else []
        raise ValueError(f"Unknown country pack: '{country}'. Available packs: {available}")
        
    try:
        with open(pack_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load country pack '{country}': {e}")
        
    if "rules" not in data or not isinstance(data["rules"], list):
        raise ValueError(f"Invalid country pack format in {pack_path}: missing 'rules' array.")
        
    return data

def get_country_rule(country: str, rule_id: str, base_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Retrieves a specific rule by ID from the specified country pack."""
    pack = load_country_pack(country, base_dir=base_dir)
    for rule in pack.get("rules", []):
        if rule.get("id") == rule_id:
            return rule
    raise KeyError(f"Rule '{rule_id}' not found in country pack '{country}'.")
