"""Small HTTP client for AnimeAPI (https://animeapi.ai)."""
import time
from typing import Any

import requests

BASE_URL = "https://animeapi.ai"
GENERATE_URL = "https://animeapi.ai/api/generate"
KEY_CHECK_URL = "https://animeapi.ai/api/videos/key-check"
USER_AGENT = "dify-plugin-animeapi/0.1.0"
TIMEOUT = 180
PRICES = {"anime": 0.003, "ultra": 0.01, "ultra-max": 0.02}


class AnimeAPIError(Exception):
    def __init__(self, message: str, code: str = "", status: int = 0):
        super().__init__(message)
        self.code = code
        self.status = status


def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": "Bearer " + api_key, "User-Agent": USER_AGENT}


def _error(response: requests.Response) -> AnimeAPIError:
    try:
        body = response.json()
    except ValueError:
        body = {}
    code = body.get("code") or "HTTP %d" % response.status_code
    message = body.get("error") or "request failed"
    if code == "INVALID_KEY":
        message += ". Check the AnimeAPI key in the plugin's authorization settings."
    elif code == "INSUFFICIENT_BALANCE":
        message += ". Add funds at https://animeapi.ai/dashboard/billing."
    return AnimeAPIError("AnimeAPI: %s (%s)" % (message, code), code, response.status_code)


def check_key(api_key: str) -> None:
    """Raise AnimeAPIError when the key is not accepted. Generates nothing."""
    try:
        response = requests.get(KEY_CHECK_URL, headers=_headers(api_key), timeout=30)
    except requests.RequestException as e:
        raise AnimeAPIError("AnimeAPI: could not reach the API (%s)" % type(e).__name__) from e
    # A valid key gets 404 for this id that does not exist; a bad key gets 401.
    if response.status_code in (401, 403):
        raise _error(response)


def generate(api_key: str, body: dict[str, Any]) -> dict[str, Any]:
    """POST /api/generate. Retries only when the API says the error is retryable."""
    error = AnimeAPIError("AnimeAPI: request failed")
    for attempt in range(3):
        if attempt:
            time.sleep(2 * attempt)
        try:
            response = requests.post(
                GENERATE_URL, json=body, headers=_headers(api_key), timeout=TIMEOUT
            )
        except requests.RequestException as e:
            error = AnimeAPIError("AnimeAPI: could not reach the API (%s)" % type(e).__name__)
            continue
        if response.ok:
            return response.json()
        error = _error(response)
        try:
            retryable = bool(response.json().get("retryable"))
        except ValueError:
            retryable = False
        if not (retryable or response.status_code in (500, 503)):
            break
    raise error


def download(url: str) -> tuple[bytes, str]:
    """Fetch a generated image from animeapi.ai. Returns (bytes, mime type)."""
    if not url.startswith(BASE_URL + "/"):
        raise AnimeAPIError("AnimeAPI: unexpected image address")
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    response.raise_for_status()
    mime = response.headers.get("Content-Type", "image/png").split(";")[0].strip() or "image/png"
    return response.content, mime
