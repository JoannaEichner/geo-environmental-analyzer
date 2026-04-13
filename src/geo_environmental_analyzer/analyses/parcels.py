from __future__ import annotations

import math

from geo_environmental_analyzer.domain.models import OrderedRoute, ParcelRecord
from geo_environmental_analyzer.domain.protocols import ParcelAnalyzer
from geo_environmental_analyzer.domain.services import (
    deduplicate_parcels,
    normalize_pl2000_coordinates,
)
from geo_environmental_analyzer.infrastructure.gateways.uldk_client import UldkClient


class DefaultParcelAnalyzer(ParcelAnalyzer):
    def __init__(self, uldk_client: UldkClient, densify_step_m: float = 50.0) -> None:
        self._uldk_client = uldk_client
        self._densify_step_m = densify_step_m

    def analyze(self, route: OrderedRoute) -> list[ParcelRecord]:
        if not route.points:
            return []
        sampled_points = self._sample_route_points(route)

        parcels: list[ParcelRecord] = []

        for x, y in sampled_points:
            for result in self._uldk_client.get_parcel_by_xy(x, y):
                parcels.append(self._parcel_from_uldk_id(result.parcel_id))
        return deduplicate_parcels(parcels)

    def _sample_route_points(self, route: OrderedRoute) -> list[tuple[float, float]]:
        normalized = [
            normalize_pl2000_coordinates(point.x_raw, point.y_raw)
            for point in route.points
        ]

        if len(normalized) == 1:
            return normalized

        sampled: list[tuple[float, float]] = []

        for index in range(len(normalized) - 1):
            x0, y0 = normalized[index]
            x1, y1 = normalized[index + 1]

            dx = x1 - x0
            dy = y1 - y0
            distance = math.sqrt(dx * dx + dy * dy)

            steps = max(1, int(math.ceil(distance / self._densify_step_m)))
            for step in range(steps):
                t = step / steps
                sampled.append((x0 + t * dx, y0 + t * dy))

        sampled.append(normalized[-1])
        return sampled

    def _parcel_from_uldk_id(self, parcel_id: str) -> ParcelRecord:
        parcel_number = self._extract_parcel_number(parcel_id)
        cadastral_district_code = self._extract_cadastral_district_code(parcel_id)
        details = self._uldk_client.get_parcel_details(parcel_id)

        return ParcelRecord(
            parcel_number=parcel_number,
            cadastral_district_code=cadastral_district_code,
            cadastral_district_name=details.cadastral_district_name if details else "",
            municipality_name=details.municipality_name if details else "",
            parcel_identifier=parcel_id,
        )

    def _extract_parcel_number(self, parcel_id: str) -> str:
        if "." not in parcel_id:
            return parcel_id

        return parcel_id.rsplit(".", 1)[-1].strip()

    def _extract_cadastral_district_code(self, parcel_id: str) -> str:
        parts = parcel_id.split(".")
        if len(parts) < 2:
            return ""
        return parts[-2].strip()
