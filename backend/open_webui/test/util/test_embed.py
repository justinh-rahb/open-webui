from types import SimpleNamespace

from open_webui.utils.embed import (
    get_embed_config,
    get_embed_panel_by_id,
    is_origin_allowed,
    normalize_allowed_origins,
)


def _model(id: str, name: str, embed: dict):
    return SimpleNamespace(id=id, name=name, meta={"embed": embed})


def test_normalize_allowed_origins():
    assert normalize_allowed_origins("https://a.com, https://b.com") == [
        "https://a.com",
        "https://b.com",
    ]
    assert normalize_allowed_origins(["https://a.com", "  "]) == ["https://a.com"]
    assert normalize_allowed_origins(None) == []


def test_get_embed_config_requires_enabled():
    model = _model("support", "Support", {"enabled": False})
    assert get_embed_config(model) is None


def test_get_embed_config_defaults_panel_id():
    model = _model("support.assistant", "Support", {"enabled": True})
    config = get_embed_config(model)
    assert config["panel_id"] == "panel-support-assistant"
    assert config["model_id"] == "support.assistant"
    assert config["title"] == "Support"


def test_get_embed_config_supports_model_dump_meta():
    class MetaModel:
        def model_dump(self):
            return {
                "embed": {
                    "enabled": True,
                    "panel_id": "panel-embed-test",
                    "allowed_origins": [],
                }
            }

    model = SimpleNamespace(id="embed-test", name="Embed Test", meta=MetaModel())
    config = get_embed_config(model)
    assert config is not None
    assert config["panel_id"] == "panel-embed-test"
    assert config["model_id"] == "embed-test"


def test_get_embed_panel_by_id(monkeypatch):
    model_a = _model("a", "A", {"enabled": True, "panel_id": "panel-a"})
    model_b = _model("b", "B", {"enabled": True, "panel_id": "panel-b"})

    monkeypatch.setattr(
        "open_webui.utils.embed.Models.get_models",
        lambda db=None: [model_a, model_b],
    )

    assert get_embed_panel_by_id("panel-b")["model_id"] == "b"
    assert get_embed_panel_by_id("unknown") is None


def test_is_origin_allowed():
    assert is_origin_allowed([], "https://a.com")
    assert is_origin_allowed(["*"], "https://a.com")
    assert is_origin_allowed(["https://a.com"], "https://a.com")
    assert not is_origin_allowed(["https://a.com"], "https://b.com")
