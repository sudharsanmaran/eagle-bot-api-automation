import logging
from datetime import datetime
from typing import List

from sqlalchemy_orm import session

from src.base.services import UserService, ListCreateUpdateRetriveDeleteService
from src.microsoft import RefreshMicrosoftToken

logger = logging.getLogger(__name__)

def recreate_expires_at(seconds: int):
    current_time_stamp = datetime.utcnow().timestamp().__int__()
    return current_time_stamp + seconds


class Authorization:
    def __init__(self, function):
        self.user = None
        self.function = function

    def __call__(self, db: session, user_name, scopes: List[str],
                 user_service: UserService, service: ListCreateUpdateRetriveDeleteService):
        self.db = db
        self.email = user_name
        self.scopes = scopes
        self.service = service
        self.user_service = user_service
        if self.check_for_availability():
            return self.retrieve_ms_token()
        else:
            return self.function(scopes)

    def refresh_access_token(self, ms_token):
        microsoft_object = RefreshMicrosoftToken(ms_token.refresh_token)
        refreshed_data = microsoft_object.refresh_access_token()
        print(refreshed_data)
        ms_token.access_token = refreshed_data['access_token']
        ms_token.refresh_token = refreshed_data['refresh_token']
        ms_token.expires_at = recreate_expires_at(refreshed_data['expires_in'])
        self.service.update(ms_token)
        return dict(access_token=refreshed_data['access_token'])

    def check_scopes(self, from_scopes):
        for scope in self.scopes:
            if scope not in from_scopes:
                return False
        return True

    def retrieve_ms_token(self) -> dict:
        ms_token = self.service.get_token_with_user_id(self.user.id)
        if ms_token:
            existing_scopes = ms_token.scopes.keys()
            if self.check_scopes(existing_scopes):
                if datetime.utcnow().timestamp().__int__() <= ms_token.expires_at:
                    return dict(access_token=ms_token.access_token)
                return self.refresh_access_token(ms_token)

        else:
            return {'error': 'Not found'}

    def check_for_availability(self) -> bool:
        try:
            self.user = self.user_service.get_by_email(self.email)

            return True if self.user else False
        except Exception as e:
            print(e)
            return False
