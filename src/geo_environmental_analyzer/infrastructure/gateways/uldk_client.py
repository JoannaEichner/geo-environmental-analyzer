from __future__ import annotations

from dataclasses import dataclass
import re

import requests
from pyproj import Transformer

from geo_environmental_analyzer.domain.services import (
    detect_epsg_2000,
    normalize_pl2000_coordinates,
)


@dataclass(slots=True)
class UldkParcelResult:
    parcel_id: str

class UldkClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    def get_parcel_by_xy(self, x: float, y: float) -> list[UldkParcelResult]:
        uldk_x, uldk_y = self._to_uldk_xy(x, y)

        response = requests.get(
            self._base_url,
            params={
                "request": "GetParcelByXY",
                "xy": f"{uldk_x:.2f},{uldk_y:.2f}",
                "result": "teryt",
            },
            timeout=self._timeout_seconds,
        )

        response.raise_for_status()
        return self._parse_parcel_response(response.text)
    
    def _parse_parcel_response(self, response_text: str) -> list[UldkParcelResult]:
        lines = [line.strip() for line in response_text.splitlines() if line.strip()]
        results: list[UldkParcelResult] = []

        for line in lines:
            if line.startswith("-1"):
                continue
            if re.fullmatch(r"[A-Za-z0-9_]+", line) and ";" not in line and "." not in line:
                continue

            match = re.match(r"^(\d{4,})", line)
            if not match:
                continue

            results.append(UldkParcelResult(parcel_id=line))

        return results
    
    def _to_uldk_xy(self, value_a: float, value_b: float) -> tuple[float, float]:
        epsg = detect_epsg_2000(value_a, value_b)
        easting, northing = normalize_pl2000_coordinates(value_a, value_b)

        if epsg == 2180:
            return easting, northing

        transformer = Transformer.from_crs(
            f"EPSG:{epsg}",
            "EPSG:2180",
            always_xy=True,
        )
        x_2180, y_2180 = transformer.transform(easting, northing)
        return x_2180, y_2180

    def get_parcel_details(self, parcel_id: str) -> UldkParcelDetails | None:
        response = requests.get(
            self._base_url,
            params={
                "request": "GetParcelById",
                "id": parcel_id,
                "result": "gmina,powiat,wojewodztwo,obreb",
            },
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        return self._parse_parcel_details(parcel_id, response.text)

    def _parse_parcel_details(
        self,
        parcel_id: str,
        response_text: str,
    ) -> UldkParcelDetails | None:
        lines = [line.strip() for line in response_text.splitlines() if line.strip()]

        for line in lines:
            if line.startswith("-1"):
                continue
            if re.fullmatch(r"[A-Za-z0-9_]+", line) and ";" not in line and "." not in line:
                continue

            parts = [part.strip() for part in line.split("|")]
            municipality_name = parts[0] if len(parts) > 0 else ""
            powiat_name = parts[1] if len(parts) > 1 else ""
            voivodeship_name = parts[2] if len(parts) > 2 else ""
            cadastral_district_name = parts[3] if len(parts) > 3 else ""

            return UldkParcelDetails(
                parcel_id=parcel_id,
                municipality_name=municipality_name,
                powiat_name=powiat_name,
                voivodeship_name=voivodeship_name,
                cadastral_district_name=cadastral_district_name,
            )

        return None

@dataclass(slots=True)
class UldkParcelDetails:
    parcel_id: str
    municipality_name: str
    powiat_name: str
    voivodeship_name: str
    cadastral_district_name: str


