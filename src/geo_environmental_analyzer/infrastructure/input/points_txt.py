from __future__ import annotations

import re
from pathlib import Path

from geo_environmental_analyzer.domain.models import InputPoint, OrderedRoute
from geo_environmental_analyzer.domain.protocols import PointReader
from geo_environmental_analyzer.domain.services import build_ordered_route


class TxtPointReader(PointReader):
    def read(self, path: Path) -> list[InputPoint]:
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        lines = path.read_text(encoding="utf-8").splitlines()
        points: list[InputPoint] = []

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            point = self._parse_line(line, line_number)

            points.append(point)

        return points

    def _parse_line(self, line: str, line_number: int) -> InputPoint:
        if "\t" in line:
            parts = [part.strip() for part in line.split("\t")]
        else:
            parts = self._split_fallback(line)
        if len(parts) < 4:
            raise ValueError(
                f"Line {line_number}: expected at least 4 columns, got {len(parts)}"
            )

        number = parts[0].strip()
        name = parts[1].strip()
        x_raw = parts[2].strip()
        y_raw = parts[3].strip()

        if not number:
            raise ValueError(f"Line {line_number}: point number is empty")
        if not name:
            raise ValueError(f"Line {line_number}: point name is empty")
        if not x_raw:
            raise ValueError(f"Line {line_number}: x coordinate is empty")
        if not y_raw:
            raise ValueError(f"Line {line_number}: y coordinate is empty")

        try:
            x_value = float(x_raw.replace(",", "."))
        except ValueError as error:
            raise ValueError(
                f"Line {line_number}: invalid x coordinate value '{x_raw}'"
            ) from error

        try:
            y_value = float(y_raw.replace(",", "."))
        except ValueError as error:
            raise ValueError(
                f"Line {line_number}: invalid y coordinate value '{y_raw}'"
            ) from error

        return InputPoint(
            number=number,
            name=name,
            x_raw=x_value,
            y_raw=y_value,
        )

    def _split_fallback(self, line: str) -> list[str]:
        if ";" in line:
            return [part.strip() for part in line.split(";")]

        return [part.strip() for part in re.split(r"\s+", line.strip())]

    def read_route(self, path: Path) -> OrderedRoute:
        points = self.read(path)
        return build_ordered_route(points)
