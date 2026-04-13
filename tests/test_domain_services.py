from __future__ import annotations

import pytest

from geo_environmental_analyzer.domain.models import InputPoint, ParcelRecord
from geo_environmental_analyzer.domain.services import (
    build_ordered_route,
    deduplicate_parcels,
    detect_epsg_2000,
    merge_min_distances,
    normalize_pl2000_coordinates,
)


def test_detect_epsg_2000_for_pl2000_coordinates() -> None:
    assert detect_epsg_2000(7450669.31, 5780467.22) == 2178


def test_detect_epsg_2000_for_reversed_pl2000_coordinates() -> None:
    assert detect_epsg_2000(5780467.22, 7450669.31) == 2178


def test_detect_epsg_2000_raises_for_invalid_coordinates() -> None:
    with pytest.raises(ValueError, match="Cannot detect PL-2000 EPSG"):
        detect_epsg_2000(1000.0, 2000.0)


def test_normalize_pl2000_coordinates_keeps_correct_axis_order() -> None:
    assert normalize_pl2000_coordinates(7450669.31, 5780467.22) == (
        7450669.31,
        5780467.22,
    )


def test_normalize_pl2000_coordinates_swaps_reversed_values() -> None:
    assert normalize_pl2000_coordinates(5780467.22, 7450669.31) == (
        7450669.31,
        5780467.22,
    )


def test_build_ordered_route_preserves_point_order() -> None:
    points = [
        InputPoint(number="1", name="A", x_raw=1.0, y_raw=2.0),
        InputPoint(number="2", name="B", x_raw=3.0, y_raw=4.0),
    ]

    route = build_ordered_route(points)

    assert [point.number for point in route.points] == ["1", "2"]


def test_build_ordered_route_raises_for_empty_input() -> None:
    with pytest.raises(ValueError, match="Cannot build route from empty points list"):
        build_ordered_route([])


def test_deduplicate_parcels_by_identifier() -> None:
    parcels = [
        ParcelRecord(
            parcel_number="194",
            cadastral_district_code="0015",
            parcel_identifier="142807_2.0015.194",
        ),
        ParcelRecord(
            parcel_number="194",
            cadastral_district_code="0015",
            parcel_identifier="142807_2.0015.194",
        ),
        ParcelRecord(
            parcel_number="195",
            cadastral_district_code="0015",
            parcel_identifier="142807_2.0015.195",
        ),
    ]

    result = deduplicate_parcels(parcels)

    assert [parcel.parcel_identifier for parcel in result] == [
        "142807_2.0015.194",
        "142807_2.0015.195",
    ]


def test_deduplicate_parcels_uses_code_and_number_fallback() -> None:
    parcels = [
        ParcelRecord(parcel_number="194", cadastral_district_code="0015"),
        ParcelRecord(parcel_number="194", cadastral_district_code="0015"),
        ParcelRecord(parcel_number="194", cadastral_district_code="0016"),
    ]

    result = deduplicate_parcels(parcels)

    assert [
        (parcel.cadastral_district_code, parcel.parcel_number) for parcel in result
    ] == [
        ("0015", "194"),
        ("0016", "194"),
    ]


def test_merge_min_distances_keeps_smaller_value() -> None:
    distances = {"Rezerwat przyrody": 1200.0}

    merge_min_distances(distances, "Rezerwat przyrody", 800.0)
    merge_min_distances(distances, "Rezerwat przyrody", 1500.0)
    merge_min_distances(distances, "Park krajobrazowy", 5000.0)

    assert distances == {
        "Rezerwat przyrody": 800.0,
        "Park krajobrazowy": 5000.0,
    }
