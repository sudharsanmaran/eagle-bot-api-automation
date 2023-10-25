
import os
import requests

from .api_urls import MicrosoftGraphURLs


class MicrosoftGraphAPI:
    def __init__(self, ms_graph_token):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {ms_graph_token}'
        }
        self.base_url = MicrosoftGraphURLs.BASE_URL.value

    def post_request(self, endpoint, data):
        url = self.construct_url(endpoint)
        response = requests.post(url, data=data, headers=self.headers)
        return response.json()

    def get_request(self, endpoint):
        url = self.construct_url(endpoint)
        response = requests.get(url, headers=self.headers)
        return response.json()

    def construct_url(self, url_enum):
        url = self.base_url + url_enum.value
        return url


class CalendarAPI(MicrosoftGraphAPI):

    def __init__(self, ms_graph_token):
        super().__init__(ms_graph_token)

    def get_schedule(self, body):
        return self.post_request(MicrosoftGraphURLs.GET_SCHEDULE, body)

    def get_calendar(self):
        return self.get_request(MicrosoftGraphURLs.GET_CALENDAR)


class EventsAPI(MicrosoftGraphAPI):

    def __init__(self, ms_graph_token):
        super().__init__(ms_graph_token)

    def create_event(self, body):
        return self.post_request(MicrosoftGraphURLs.CREATE_EVENT, body)


class EmailAPI(MicrosoftGraphAPI):

    def __init__(self, ms_graph_token):
        super().__init__(ms_graph_token)

    def send_email(self, body):
        response = self.post_request(MicrosoftGraphURLs.SEND_MAIL, body)
        return "Sent Successfully" if response.status_code == 202 else 'Failed to send'


class UserAPI(MicrosoftGraphAPI):

    def __init__(self, ms_graph_token):
        super().__init__(ms_graph_token)

    def get_user(self):
        response = self.get_request(MicrosoftGraphURLs.USER_DETAILS)
        return response
