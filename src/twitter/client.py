import tweepy

class TwitterClient:
  def __init__(self):
    self.client_id = 'UERRTDJlNzNkX0xrNE1pZW0xa3E6MTpjaQ'
    self.client_secret = 'VMIYL2CEIYqHAuxTlHUMeiTnATTmNxKlmAdSKVmRyxbu-M4cKI'
    self.redirect_uri = 'https://google.com'

  def get_consent_url(self, scopes):
    """Generates an authorization URL for the specified scopes."""

    self.auth = tweepy.OAuth2UserHandler(
      client_id=self.client_id,
      redirect_uri=self.redirect_uri,
      scope=scopes,
    )

    return self.auth.get_authorization_url()

  def exchange_code_for_tokens(self, code):
    """Exchanges an authorization code for an access token."""

    return self.auth.fetch_token(code)

  def get_client(self, access_token):
    """Creates a Twitter API client using the specified access token."""

    return tweepy.Client(access_token=access_token)
  

