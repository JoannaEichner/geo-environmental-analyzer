from __future__ import annotations

from pathlib import Path

import pytest

from geo_environmental_analyzer.infrastructure.input.points_txt import TxtPointReader


def test_read_parses_tab_separated_points(tmp_path: Path) -> None:
    input_path = tmp_path / "points.txt"
    input_path.write_text(
        "1\tP1\t7450669,31\t5780467,22\n2\tP2\t7450700.00\t5780500.00\n"
    )

    points = TxtPointReader().read(input_path)

    assert len(points) == 2
    assert points[0].number == "1"
    assert points[0].name == "P1"
    assert points[0].x_raw == 7450669.31
    assert points[0].y_raw == 5780467.22


def test_read_supports_semicolon_fallback(tmp_path: Path) -> None:
    input_path = tmp_path / "points_semicolon.txt"
    input_path.write_text("1;P1;7450669.31;5780467.22\n")

    points = TxtPointReader().read(input_path)

    assert len(points) == 1
    assert points[0].number == "1"
    assert points[0].name == "P1"


def test_read_skips_blank_lines(tmp_path: Path) -> None:
    input_path = tmp_path / "points_blank_lines.txt"
    input_path.write_text("\n1\tP1\t7450669.31\t5780467.22\n\n")

    points = TxtPointReader().read(input_path)

    assert len(points) == 1


def test_read_route_builds_ordered_route(tmp_path: Path) -> None:
    input_path = tmp_path / "points_route.txt"
    input_path.write_text(
        "1\tP1\t7450669.31\t5780467.22\n2\tP2\t7450700.00\t5780500.00\n"
    )

    route = TxtPointReader().read_route(input_path)

    assert [point.number for point in route.points] == ["1", "2"]


def test_read_raises_for_missing_file(tmp_path: Path) -> None:
    input_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError, match="Input file not found"):
        TxtPointReader().read(input_path)


def test_read_raises_for_too_few_columns(tmp_path: Path) -> None:
    input_path = tmp_path / "too_few_columns.txt"
    input_path.write_text("1\tP1\t7450669.31\n")

    with pytest.raises(ValueError, match="Line 1: expected at least 4 columns, got 3"):
        TxtPointReader().read(input_path)


def test_read_raises_for_empty_point_name(tmp_path: Path) -> None:
    input_path = tmp_path / "empty_name.txt"
    input_path.write_text("1\t\t7450669.31\t5780467.22\n")

    with pytest.raises(ValueError, match="Line 1: point name is empty"):
        TxtPointReader().read(input_path)


def test_read_raises_for_invalid_x_coordinate(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid_x.txt"
    input_path.write_text("1\tP1\tnot-a-number\t5780467.22\n")

    with pytest.raises(
        ValueError, match="Line 1: invalid x coordinate value 'not-a-number'"
    ):
        TxtPointReader().read(input_path)


def test_read_raises_for_invalid_y_coordinate(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid_y.txt"
    input_path.write_text("1\tP1\t7450669.31\tbad-value\n")

    with pytest.raises(
        ValueError, match="Line 1: invalid y coordinate value 'bad-value'"
    ):
        TxtPointReader().read(input_path)
