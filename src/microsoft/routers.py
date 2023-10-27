import json

from fastapi import APIRouter, Depends

from .client import CalendarAPI
from .dependencies import token_service, user_service
from .methods import get_busy_or_free_schedule_scopes
from .schemas import GetFreeOrBusySchedule, DateTimeField
from .services import MicrosoftTokenService
from .utils import get_access_token_or_url, authorize_user
from ..auth import JWTBearer
from ..database import get_db

microsoft_router = APIRouter(tags=["microsoft"], prefix="/v1/microsoft")


@microsoft_router.post('/get_busy_or_free_schedules')
async def retrieve_url_or_token(
        get_schedules: GetFreeOrBusySchedule,
        db=Depends(get_db),
        user=Depends(JWTBearer()),
        service: MicrosoftTokenService = Depends(token_service),
        _user_service=Depends(user_service)
):
    user_name = user[0]['email']
    scopes = get_busy_or_free_schedule_scopes()[:-1]
    data = get_access_token_or_url(
        db=db, scopes=scopes, user_name=user_name,
        user_service=_user_service, service=service
    )
    if data:
        if 'access_token' in data.keys():
            calendar_api = CalendarAPI(data['access_token'])
            json_data = get_schedules.__dict__
            for i in json_data.keys():
                if type(json_data[i]) == DateTimeField:
                    json_data[i] = json_data[i].__dict__
            print(json_data)
            return calendar_api.get_schedule(json.dumps(json_data))
        return data
    else:
        return {'error': data}


@microsoft_router.post('/auth_code')
async def retrieve_access_token(
        code: str,
        user=Depends(JWTBearer()),
        service: MicrosoftTokenService = Depends(token_service),
        _user_service=Depends(user_service)
):
    return authorize_user(code, service, _user_service, user)
    # return dict(status='User authorized.')
