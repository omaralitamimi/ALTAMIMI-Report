from __future__ import annotations

from urllib.parse import urlparse

PLATFORM_HELP = {
    "Facebook": "https://www.facebook.com/help/",
    "Instagram": "https://help.instagram.com/",
    "X / Twitter": "https://help.x.com/",
    "TikTok": "https://support.tiktok.com/",
}


def normalize_url(value: str) -> str:
    value = value.strip()
    if value and "://" not in value:
        value = "https://" + value
    return value


def is_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False
