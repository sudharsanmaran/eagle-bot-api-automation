from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .utils import get_access_token_or_url, authorize_user
from src.base.utils import Platform
from .client import CalendarAPI
from .methods import get_busy_or_free_schedule_scopes
from .schemas import GetFreeOrBusySchedule
from .services import MicrosoftTokenService
from ..database import get_db
from ..auth import JWTBearer
from .dependencies import token_service, user_service

microsoft_router = APIRouter(tags=["microsoft"], prefix="/v1/microsoft")


@microsoft_router.post('/get_busy_or_free_schedules')
async def retrieve_url_or_token(
        get_schedules: GetFreeOrBusySchedule,
        db=Depends(get_db),
        user=Depends(JWTBearer()),
        service: MicrosoftTokenService = Depends(token_service),
):
    print(user)
    user_name = ''  # need to change
    scopes = get_busy_or_free_schedule_scopes()
    data = get_access_token_or_url(db=db, platform=Platform.MICROSOFT.value, scopes=scopes, user_name=user_name)
    if 'access_token' in data.keys():
        calendar_api = CalendarAPI(data['access_token'])
        return calendar_api.get_schedule(get_schedules)
    return data


@microsoft_router.post('/auth_code')
async def retrieve_access_token(
        code: str,
        user=Depends(JWTBearer()),
        service: MicrosoftTokenService = Depends(token_service),
        _user_service=Depends(user_service)
):
    return authorize_user(code, service, _user_service, user[0])
    # return dict(status='User authorized.')
