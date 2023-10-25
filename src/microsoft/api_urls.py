from enum import Enum


class MicrosoftGraphURLs(Enum):
    BASE_URL = 'https://graph.microsoft.com/v1.0/'
    GET_SCHEDULE = 'me/calendar/getschedule'
    GET_CALENDAR = 'me/calendar'
    CREATE_EVENT = 'me/events'
    SEND_MAIL = 'me/sendMail'
    USER_DETAILS = 'me/'


class InitialMicrosoftGraphURLs(Enum):
    BASE_URL = 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/'
    AUTHORIZE = 'authorize'
    TOKEN_URL = 'token'
