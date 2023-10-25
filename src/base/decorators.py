import logging
from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy_orm import session

from src.base.utils import Platform
from src.microsoft import RefreshMicrosoftToken
from src.microsoft.models import MicrosoftToken

logger = logging.getLogger(__name__)


class Authorization:
    def __init__(self, function):
        self.table = None
        self.function = function

    def __call__(self, db: session, user_name, platform: str, scopes: List[str]):
        self.db = db
        self.user_name = user_name
        self.platform = platform
        self.scopes = scopes
        if self.check_for_availability():
            return self.retrieve_token_with_username()
        else:
            return self.function(platform, scopes)

    def refresh_access_token(self, refresh_token: str):
        if Platform.MICROSOFT.value == self.platform:
            microsoft_object = RefreshMicrosoftToken(refresh_token)
            refreshed_data = microsoft_object.refresh_access_token()
            # todo Need to store to db
            return dict(access_token=refreshed_data['access_token'])

        elif Platform.GOOGLE.value == self.platform:
            # todo Need to update
            pass
            # google_object = RefreshGoogleToken(refresh_token)
            # return google_object.refresh_access_token()
        elif Platform.JIRA.value == self.platform:
            # todo Need to update
            pass

    def check_scopes(self, from_scopes):
        for scope in self.scopes:
            if scope not in from_scopes:
                return False
        return True

    def retrieve_token_with_username(self) -> dict:
        try:
            stmt = select(self.table).where(
                getattr(self.table, 'email') == self.user_name)

            with self.db:
                token_info = self.db.execute(stmt).scalar_one()
                existing_scopes = eval(token_info.scopes) if token_info.scopes != '' else []
                if self.check_scopes(existing_scopes):
                    if datetime.utcnow().timestamp().__int__() <= token_info.expires_at:
                        return dict(access_token=token_info.access_token)
                    return self.refresh_access_token(token_info.__refresh_token)
        except NoResultFound:
            logger.info(
                f"No result found for model {self.table} with primary key {self.user_name}")
            return dict(error=f"No result found for model {self.table} with primary key {self.user_name}")

    def check_for_availability(self) -> bool:
        try:
            self.table = self.get_table_using_platform()
            stmt = select(self.table).where(getattr(self.table, 'email') == self.user_name)
            with self.db:
                token_info = self.db.execute(stmt).scalar_one()
            return True if token_info else False
        except Exception as e:
            print(e)
            return False

    def get_table_using_platform(self):
        if self.platform == Platform.MICROSOFT.value:
            return MicrosoftToken
        elif self.platform == Platform.GOOGLE.value:
            # return GoogleToken
            # todo need to change
            return
        elif self.platform == Platform.JIRA.value:
            # todo need to change
            return
