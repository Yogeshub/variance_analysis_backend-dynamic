import os
import httpx

# Default: secure
SSL_VERIFY = os.getenv("SSL_VERIFY", "true").lower() == "true"


def get_http_client() -> httpx.Client:
    return httpx.Client(verify=SSL_VERIFY, timeout=httpx.Timeout(30.0))


def get_async_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(verify=SSL_VERIFY, timeout=httpx.Timeout(30.0))
