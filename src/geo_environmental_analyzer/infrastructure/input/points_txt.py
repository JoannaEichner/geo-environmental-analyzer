from __future__ import annotations

import re
from pathlib import Path

from geo_environmental_analyzer.domain.models import InputPoint
from geo_environmental_analyzer.domain.protocols import PointReader

class TxtPointReader(PointReader):
    def read(self, path: Path) -> list[InputPoint]:
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        lines = path.read_text(encoding="utf-8").splitlines()
        points: list[InputPoint] = []

        for line in lines:
            if not line.strip():
                continue
            point = self._parse_line(line)
            points.append(point)

        return points
    
    def _parse_line(self, line: str) -> InputPoint:
        if "\t" in line:
            parts = [part.strip() for part in line.split("\t")]
        else:
            parts = self._split_fallback(line)
        if len(parts) < 4:
            raise ValueError(f"Invalid input row: {line}")
        
        return InputPoint(
            number=parts[0],
            name=parts[1],
            x_raw=float(parts[2].replace(",", ".")),
            y_raw=float(parts[3].replace(",", ".")),
        )
    
    def _split_fallback(self, line: str) -> list[str]:
        if ";" in line:
            return [part.strip() for part in line.split(";")]

        return [part.strip() for part in re.split(r"\s+", line.strip())]








