from datetime import datetime, timedelta
import os
from typing import Dict
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
import base64


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, request_limit: int = 100, interval: timedelta = timedelta(minutes=1)):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.request_limit = request_limit
        self.interval = interval
        self.requests: Dict[str, list] = {}

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme.")
            is_verified, payload = self.verify_jwt(credentials.credentials)
            if not is_verified:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token.")
            self.rate_limit(credentials.credentials)
            return payload, credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid, payload

    def rate_limit(self, token: str):
        if token not in self.requests:
            self.requests[token] = []
        self.requests[token].append(datetime.now())
        self.requests[token] = [d for d in self.requests[token] if d > datetime.now() - self.interval]
        if len(self.requests[token]) > self.request_limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
            )


def generateJWT(payload) -> str:
    token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm=os.getenv('JWT_ALGORITHM'))
    return token


def decodeJWT(token: str) -> dict:
    try:

        base64_encoded_string = os.getenv('JWT_SECRET_KEY')
        decoded_bytes = base64.b64decode(base64_encoded_string)
        pub_decoded_string = decoded_bytes.decode('utf-8')

        return jwt.decode(token, pub_decoded_string, algorithms=[os.getenv('JWT_ALGORITHM')], audience="Client_Identity", issuer="EagleBOT")
    except:
        return {}
