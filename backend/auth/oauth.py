from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx
import structlog

from core.config import settings
from core.redis import redis_manager

log = structlog.get_logger()


@dataclass
class OAuthUserInfo:
    provider: str
    provider_user_id: str
    email: str | None
    full_name: str | None
    username: str | None
    avatar_url: str | None
    raw_data: dict[str, Any]
    access_token: str | None = None
    refresh_token: str | None = None


class OAuthProvider:
    """Abstract base for OAuth providers."""

    name: str
    authorization_url: str
    token_url: str
    userinfo_url: str
    scopes: list[str]

    def __init__(self) -> None:
        self._client_id = ""
        self._client_secret = ""
        self._redirect_uri = ""

    def get_authorization_url(self, state: str) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "state": state,
        }
        return f"{self.authorization_url}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "code": code,
                    "redirect_uri": self._redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    def parse_user_info(self, data: dict, tokens: dict) -> OAuthUserInfo:
        raise NotImplementedError


class GoogleOAuthProvider(OAuthProvider):
    name = "google"
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    scopes = ["openid", "email", "profile"]

    def __init__(self) -> None:
        super().__init__()
        self._client_id = settings.GOOGLE_CLIENT_ID
        self._client_secret = settings.GOOGLE_CLIENT_SECRET
        self._redirect_uri = settings.GOOGLE_REDIRECT_URI

    def get_authorization_url(self, state: str) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.authorization_url}?{urlencode(params)}"

    def parse_user_info(self, data: dict, tokens: dict) -> OAuthUserInfo:
        return OAuthUserInfo(
            provider=self.name,
            provider_user_id=data["id"],
            email=data.get("email"),
            full_name=data.get("name"),
            username=None,
            avatar_url=data.get("picture"),
            raw_data=data,
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
        )


class GitHubOAuthProvider(OAuthProvider):
    name = "github"
    authorization_url = "https://github.com/login/oauth/authorize"
    token_url = "https://github.com/login/oauth/access_token"
    userinfo_url = "https://api.github.com/user"
    scopes = ["user:email", "read:user"]

    def __init__(self) -> None:
        super().__init__()
        self._client_id = settings.GITHUB_CLIENT_ID
        self._client_secret = settings.GITHUB_CLIENT_SECRET
        self._redirect_uri = settings.GITHUB_REDIRECT_URI

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            user_resp = await client.get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github.v3+json"},
            )
            user_resp.raise_for_status()
            user_data = user_resp.json()

            # Fetch primary email if not public
            if not user_data.get("email"):
                email_resp = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                emails = email_resp.json()
                primary = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
                user_data["email"] = primary

            return user_data

    def parse_user_info(self, data: dict, tokens: dict) -> OAuthUserInfo:
        return OAuthUserInfo(
            provider=self.name,
            provider_user_id=str(data["id"]),
            email=data.get("email"),
            full_name=data.get("name"),
            username=data.get("login"),
            avatar_url=data.get("avatar_url"),
            raw_data=data,
            access_token=tokens.get("access_token"),
        )


class DiscordOAuthProvider(OAuthProvider):
    name = "discord"
    authorization_url = "https://discord.com/api/oauth2/authorize"
    token_url = "https://discord.com/api/oauth2/token"
    userinfo_url = "https://discord.com/api/users/@me"
    scopes = ["identify", "email"]

    def __init__(self) -> None:
        super().__init__()
        self._client_id = settings.DISCORD_CLIENT_ID
        self._client_secret = settings.DISCORD_CLIENT_SECRET
        self._redirect_uri = settings.DISCORD_REDIRECT_URI

    def parse_user_info(self, data: dict, tokens: dict) -> OAuthUserInfo:
        avatar = None
        if data.get("avatar"):
            avatar = f"https://cdn.discordapp.com/avatars/{data['id']}/{data['avatar']}.png"
        return OAuthUserInfo(
            provider=self.name,
            provider_user_id=data["id"],
            email=data.get("email"),
            full_name=data.get("global_name") or data.get("username"),
            username=data.get("username"),
            avatar_url=avatar,
            raw_data=data,
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
        )


class LinkedInOAuthProvider(OAuthProvider):
    name = "linkedin"
    authorization_url = "https://www.linkedin.com/oauth/v2/authorization"
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    userinfo_url = "https://api.linkedin.com/v2/me"
    scopes = ["r_liteprofile", "r_emailaddress"]

    def __init__(self) -> None:
        super().__init__()
        self._client_id = settings.LINKEDIN_CLIENT_ID
        self._client_secret = settings.LINKEDIN_CLIENT_SECRET
        self._redirect_uri = settings.LINKEDIN_REDIRECT_URI

    def parse_user_info(self, data: dict, tokens: dict) -> OAuthUserInfo:
        first = data.get("localizedFirstName", "")
        last = data.get("localizedLastName", "")
        return OAuthUserInfo(
            provider=self.name,
            provider_user_id=data["id"],
            email=None,
            full_name=f"{first} {last}".strip() or None,
            username=None,
            avatar_url=None,
            raw_data=data,
            access_token=tokens.get("access_token"),
        )


class MetaOAuthProvider(OAuthProvider):
    name = "meta"
    authorization_url = "https://www.facebook.com/v18.0/dialog/oauth"
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    userinfo_url = "https://graph.facebook.com/me?fields=id,name,email,picture"
    scopes = ["email", "public_profile"]

    def __init__(self) -> None:
        super().__init__()
        self._client_id = settings.META_CLIENT_ID
        self._client_secret = settings.META_CLIENT_SECRET
        self._redirect_uri = settings.META_REDIRECT_URI

    def parse_user_info(self, data: dict, tokens: dict) -> OAuthUserInfo:
        return OAuthUserInfo(
            provider=self.name,
            provider_user_id=data["id"],
            email=data.get("email"),
            full_name=data.get("name"),
            username=None,
            avatar_url=data.get("picture", {}).get("data", {}).get("url"),
            raw_data=data,
            access_token=tokens.get("access_token"),
        )


# Provider registry
OAUTH_PROVIDERS: dict[str, OAuthProvider] = {
    "google": GoogleOAuthProvider(),
    "github": GitHubOAuthProvider(),
    "discord": DiscordOAuthProvider(),
    "linkedin": LinkedInOAuthProvider(),
    "meta": MetaOAuthProvider(),
}


async def generate_oauth_state(provider: str) -> str:
    state = secrets.token_urlsafe(32)
    await redis_manager.set(f"oauth:state:{state}", provider, ttl=600)
    return state


async def verify_oauth_state(state: str) -> str | None:
    provider = await redis_manager.get(f"oauth:state:{state}")
    if provider:
        await redis_manager.delete(f"oauth:state:{state}")
    return provider


async def process_oauth_callback(provider_name: str, code: str) -> OAuthUserInfo:
    provider = OAUTH_PROVIDERS.get(provider_name)
    if not provider:
        raise ValueError(f"Unknown OAuth provider: {provider_name}")

    tokens = await provider.exchange_code(code)
    access_token = tokens.get("access_token")
    if not access_token:
        raise ValueError("No access token received from OAuth provider")

    user_data = await provider.get_user_info(access_token)
    return provider.parse_user_info(user_data, tokens)
