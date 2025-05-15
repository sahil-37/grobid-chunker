# app/grobid_client.py

import requests
from app.models import GROBID_URL

def send_to_grobid(pdf_bytes):
    """Send a PDF file to GROBID server and receive TEI XML."""
    response = requests.post(
        GROBID_URL,
        files={"input": pdf_bytes},
        headers={"Accept": "application/xml"},
        timeout=60
    )
    if response.status_code == 200:
        return response.text
    else:
        print(f"❌ GROBID failed with status code {response.status_code}")
        return None
