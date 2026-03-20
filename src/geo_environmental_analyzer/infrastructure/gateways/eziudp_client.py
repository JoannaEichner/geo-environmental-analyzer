from __future__ import annotations

from dataclasses import dataclass
import re

import requests

@dataclass(slots=True)
class EziudpWfsResult:
    powiat_code: str
    wfs_url: str

class EziudpClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    def get_wfs_url_for_powiat(self, powiat_code: str) -> str | None:
        response = requests.get(
            self._base_url,
            params={
                "teryt": powiat_code,
                "rodzaj": "powiaty",
            },
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()

        return self._parse_wfs_url(response.text)
    def _parse_wfs_url(self, response_text: str) -> str | None:
        match = re.search(r"https?://[^\s\"'<>]+", response_text)
        if not match:
            return None
        return match.group(0)


