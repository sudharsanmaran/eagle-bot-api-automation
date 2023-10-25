import os
from abc import ABC

import requests

from src.microsoft.methods import generate_json_for_refresh_token
from src.base.utils import Platform
from src.microsoft.api_urls import InitialMicrosoftGraphURLs


class RefreshMicrosoftToken:
    def __init__(self, refresh_token):
        self.refresh_token = refresh_token
        self.base_url = InitialMicrosoftGraphURLs.BASE_URL.value
        self.tenant = os.environ.get('MICROSOFT_TENANT_ID')

    def refresh_access_token(self) -> dict:
        url = (self.base_url+InitialMicrosoftGraphURLs.TOKEN_URL).format(tenant=self.tenant)
        data = generate_json_for_refresh_token(Platform.MICROSOFT.value, self.refresh_token)

        response = requests.post(url, data=data)
        return response.json()