import re
from typing import Any, Optional

from sqlalchemy.orm import Session

from open_webui.models.models import Models


def _to_slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "-", value).strip("-").lower()


def _as_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if value is None:
        return {}
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        return dumped if isinstance(dumped, dict) else {}
    return {}


def normalize_allowed_origins(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(origin).strip() for origin in value if str(origin).strip()]
    if isinstance(value, str):
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    return []


def get_embed_config(model: Any) -> Optional[dict]:
    meta = _as_dict(getattr(model, "meta", None)).copy()
    embed = _as_dict(meta.get("embed")).copy()

    if not embed.get("enabled", False):
        return None

    panel_id = str(
        embed.get("panel_id") or f"panel-{_to_slug(getattr(model, 'id', ''))}"
    )
    auth_mode = str(embed.get("auth_mode") or "external_jwt")

    return {
        "panel_id": panel_id,
        "model_id": str(getattr(model, "id", "")),
        "title": str(embed.get("title") or getattr(model, "name", "")),
        "welcome_message": embed.get("welcome_message"),
        "starter_prompts": embed.get("starter_prompts") or [],
        "allow_anonymous": bool(embed.get("allow_anonymous", False)),
        "auth_mode": auth_mode,
        "allowed_origins": normalize_allowed_origins(embed.get("allowed_origins")),
        "ui": embed.get("ui") if isinstance(embed.get("ui"), dict) else {},
    }


def get_embed_panel_by_id(
    panel_id: str, db: Optional[Session] = None
) -> Optional[dict]:
    for model in Models.get_models(db=db):
        config = get_embed_config(model)
        if config and config["panel_id"] == panel_id:
            return config
    return None


def is_origin_allowed(allowed_origins: list[str], origin: Optional[str]) -> bool:
    if not allowed_origins:
        return True
    if origin is None:
        return False
    return "*" in allowed_origins or origin in allowed_origins
