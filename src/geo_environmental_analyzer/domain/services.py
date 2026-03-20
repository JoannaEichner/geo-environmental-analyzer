from __future__ import annotations

from geo_environmental_analyzer.domain.models import InputPoint, OrderedRoute, ParcelRecord

ZONE_EPSG = {
    5: 2176,
    6: 2177,
    7: 2178,
    8: 2179,
}

def detect_epsg_2000(value_a: float, value_b: float) -> int:
    for candidate in (value_a, value_b):
        zone = int(str(abs(int(candidate)))[0])
        if zone in ZONE_EPSG and 5_000_000 <= candidate <= 9_000_000:
            other = value_b if candidate == value_a else value_a
            if 5_300_000 <= other <= 7_700_000:
                return ZONE_EPSG[zone]
            
    easting = max(value_a, value_b)
    zone = int(str(abs(int(easting)))[0])
    if zone in ZONE_EPSG:
        return ZONE_EPSG[zone]
    
    raise ValueError(
        f"Cannot detect PL-2000 EPSG for coordinates: {value_a}, {value_b}"
    )

def normalize_pl2000_coordinates(value_a: float, value_b: float) -> tuple[float, float]:
    zone_a = int(str(abs(int(value_a)))[0]) if 5_000_000 <= value_a <= 9_000_000 else 0
    zone_b = int(str(abs(int(value_b)))[0]) if 5_000_000 <= value_b <= 9_000_000 else 0

    if zone_a in ZONE_EPSG:
        return value_a, value_b
    if zone_b in ZONE_EPSG:
        return value_b, value_a

    if value_a >= value_b:
        return value_a, value_b
    return value_b, value_a

def build_ordered_route(points: list[InputPoint]) -> OrderedRoute:
    if not points:
        raise ValueError("Cannot build route from empty points list")
    return OrderedRoute(points=list(points))

def deduplicate_parcels(parcels: list[ParcelRecord]) -> list[ParcelRecord]:
    seen_identifiers: set[str] = set()
    unique_parcels: list[ParcelRecord] = []

    for parcel in parcels:
        key = parcel.parcel_identifier.strip() or (f"{parcel.cadastral_district}::{parcel.parcel_number}")

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
