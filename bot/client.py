from __future__ import annotations

import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot.client")

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when Binance returns an error or the network fails."""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str,
                 base_url: str = TESTNET_BASE_URL, timeout: int = 10):

        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret are both required.")

        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

        # Reuse one HTTP session for efficiency
        self._session = requests.Session()
        self._session.headers.update({
            "X-MBX-APIKEY": self._api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.info("Client ready → %s", self._base_url)

    # ── Public methods ────────────────────────────────────────────────

    def get_server_time(self) -> int:
        data = self._get("/fapi/v1/time", signed=False)
        return data["serverTime"]

    def place_order(self, params: dict) -> dict:
        logger.info("Sending order → %s", params)
        return self._post("/fapi/v1/order", params, signed=True)

    # ── Private HTTP helpers ──────────────────────────────────────────

    def _get(self, path: str, params: dict = None, signed: bool = False) -> dict:
        url = self._base_url + path
        query = dict(params or {})
        if signed:
            query = self._sign(query)
        logger.debug("GET %s | params=%s", url, query)
        try:
            resp = self._session.get(url, params=query, timeout=self._timeout)
        except requests.exceptions.RequestException as e:
            logger.error("Network error: %s", e)
            raise BinanceClientError(f"Network error: {e}") from e
        return self._parse(resp)

    def _post(self, path: str, params: dict = None, signed: bool = False) -> dict:
        url = self._base_url + path
        body = dict(params or {})
        if signed:
            body = self._sign(body)
        logger.debug("POST %s | body=%s", url, body)
        try:
            resp = self._session.post(url, data=body, timeout=self._timeout)
        except requests.exceptions.RequestException as e:
            logger.error("Network error: %s", e)
            raise BinanceClientError(f"Network error: {e}") from e
        return self._parse(resp)

    def _sign(self, params: dict) -> dict:
        """Add timestamp and HMAC-SHA256 signature to the params."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    @staticmethod
    def _parse(resp: requests.Response) -> dict:
        """Parse the response and raise on any error."""
        logger.debug("Response %s | %s", resp.status_code, resp.text[:400])
        try:
            data = resp.json()
        except ValueError:
            raise BinanceClientError(
                f"Non-JSON response (HTTP {resp.status_code}): {resp.text[:200]}",
                status_code=resp.status_code,
            )

        # Binance returns error dicts with a negative "code" field
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            code = data.get("code")
            msg  = data.get("msg", "Unknown error")
            logger.error("Binance API error %s: %s", code, msg)
            raise BinanceClientError(
                f"Binance error {code}: {msg}",
                status_code=resp.status_code,
                response=data,
            )

        if not resp.ok:
            raise BinanceClientError(
                f"HTTP {resp.status_code}: {resp.text[:200]}",
                status_code=resp.status_code,
            )

        return data