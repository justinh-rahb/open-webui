import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from open_webui.constants import ERROR_MESSAGES
from open_webui.internal.db import get_session
from open_webui.utils.embed import get_embed_panel_by_id, is_origin_allowed

log = logging.getLogger(__name__)

router = APIRouter()


class EmbedPanelResponse(BaseModel):
    id: str
    model_id: str
    title: str
    welcome_message: Optional[str] = None
    starter_prompts: list[str] = []
    auth_mode: str
    allow_anonymous: bool = False
    allowed_origins: list[str] = []
    ui: dict = {}


@router.get("/panels/{panel_id}", response_model=EmbedPanelResponse)
async def get_embed_panel(
    request: Request,
    panel_id: str,
    db: Session = Depends(get_session),
):
    if not request.app.state.config.ENABLE_EMBED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    panel = get_embed_panel_by_id(panel_id, db=db)
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    origin = request.headers.get("origin")
    if not is_origin_allowed(panel["allowed_origins"], origin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    return EmbedPanelResponse(
        id=panel["panel_id"],
        model_id=panel["model_id"],
        title=panel["title"],
        welcome_message=panel["welcome_message"],
        starter_prompts=panel["starter_prompts"],
        auth_mode=panel["auth_mode"],
        allow_anonymous=panel["allow_anonymous"],
        allowed_origins=panel["allowed_origins"],
        ui=panel["ui"],
    )
