# app/grobid_client.py

import logging
from typing import Optional

import httpx
import backoff
from httpx import ConnectError, ReadTimeout, HTTPStatusError

from app.models import GROBID_URL

logger = logging.getLogger(__name__)

# Shared async client – will be initialized once
_client: Optional[httpx.AsyncClient] = None

def get_client() -> httpx.AsyncClient:
    """
    Lazily initialize and return the shared HTTP client.
    Ensures client is only created once.
    """
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client

@backoff.on_exception(
    backoff.expo,
    (ConnectError, ReadTimeout),
    max_tries=5,
    jitter=None,
)
async def send_to_grobid_async(pdf_bytes: bytes) -> str:
    """
    Send PDF to GROBID and return TEI XML string.
    Retries on transient connection issues (e.g., timeout, refused).
    """
    client = get_client()

    try:
        files = {"input": ("file.pdf", pdf_bytes, "application/pdf")}
        headers = {"Accept": "application/xml"}  # GROBID returns XML

        response = await client.post(GROBID_URL, files=files, headers=headers)

        if response.status_code == 503:
            logger.warning("⚠️ GROBID overloaded (503). Retry may help.")
            raise RuntimeError("GROBID overloaded (503)")

        response.raise_for_status()
        return response.text

    except HTTPStatusError as e:
        status = e.response.status_code
        logger.error(f"❌ GROBID HTTP error {status}: {e.response.text}")
        raise

    except Exception as e:
        logger.error(f"❌ GROBID request failed: {e}")
        raise

async def close_grobid_client():
    """Gracefully close the shared async client (call during app shutdown)."""
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None
