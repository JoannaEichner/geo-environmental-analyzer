from __future__ import annotations

from geo_environmental_analyzer.domain.models import InputPoint, OrderedRoute, ParcelRecord

ZONE_EPSG = {
    5: 2176,
    6: 2177,
    7: 2178,
    8: 2179,
}

def detect_epsg_2000(value_a: float, value_b: float) -> int:
    def zone_digit(value: float) -> int:
        if 5_000_000 <= value <= 9_000_000:
            return int(str(abs(int(value)))[0])
        return 0

    def looks_like_northing(value: float) -> bool:
        return 5_300_000 <= value <= 7_700_000

    zone_a = zone_digit(value_a)
    zone_b = zone_digit(value_b)

    if zone_a in ZONE_EPSG and zone_b not in ZONE_EPSG and looks_like_northing(value_b):
        return ZONE_EPSG[zone_a]

    if zone_b in ZONE_EPSG and zone_a not in ZONE_EPSG and looks_like_northing(value_a):
        return ZONE_EPSG[zone_b]

    if zone_a in ZONE_EPSG and zone_b in ZONE_EPSG:
        if value_a > value_b and looks_like_northing(value_b):
            return ZONE_EPSG[zone_a]
        if value_b > value_a and looks_like_northing(value_a):
            return ZONE_EPSG[zone_b]

    raise ValueError(
        f"Cannot detect PL-2000 EPSG for coordinates: {value_a}, {value_b}"
    )

def normalize_pl2000_coordinates(value_a: float, value_b: float) -> tuple[float, float]:
    epsg = detect_epsg_2000(value_a, value_b)
    expected_zone = epsg - 2171

    def zone_digit(value: float) -> int:
        if 5_000_000 <= value <= 9_000_000:
            return int(str(abs(int(value)))[0])
        return 0

    zone_a = zone_digit(value_a)
    zone_b = zone_digit(value_b)

    if zone_a == expected_zone:
        return value_a, value_b
    if zone_b == expected_zone:
        return value_b, value_a

    raise ValueError(
        f"Cannot normalize PL-2000 coordinates for values: {value_a}, {value_b}"
    )


def build_ordered_route(points: list[InputPoint]) -> OrderedRoute:
    if not points:
        raise ValueError("Cannot build route from empty points list")
    return OrderedRoute(points=list(points))

def deduplicate_parcels(parcels: list[ParcelRecord]) -> list[ParcelRecord]:
    seen_identifiers: set[str] = set()
    unique_parcels: list[ParcelRecord] = []

    for parcel in parcels:
        key = parcel.parcel_identifier.strip() or (f"{parcel.cadastral_district_code}::{parcel.parcel_number}")

        if key in seen_identifiers:
            continue
        seen_identifiers.add(key)
        unique_parcels.append(parcel)

    return unique_parcels

def merge_min_distances(distances: dict[str, float], name: str, value: float) -> dict[str, float]:
    current = distances.get(name)
    if current is None or value < current:
        distances[name] = value
    return distances
