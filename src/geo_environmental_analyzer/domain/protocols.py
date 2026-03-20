from __future__ import annotations

from pathlib import Path
from typing import Protocol

from geo_environmental_analyzer.domain.models import (
    AnalysisBundle,
    GroundWaterResult,
    InputPoint,
    OrderedRoute,
    ParcelRecord,
    ProtectedAreaDistance,
    SurfaceWaterResult,
)

class PointReader(Protocol):
    def read(self, path: Path) -> list[InputPoint]:
        ...

class RouteBuilder(Protocol):
    def build(self, points: list[InputPoint]) -> OrderedRoute:
        ...

class ParcelAnalyzer(Protocol):
    def analyze(self, route: OrderedRoute) -> list[ParcelRecord]:
        ...

class ProtectedAreaAnalyzer(Protocol):
    def analyze(self, route: OrderedRoute) -> list[ProtectedAreaDistance]:
        ...

class ReportWriter(Protocol):
    def write(self, bundle: AnalysisBundle, output_path: Path) -> None:
        ...

class SurfaceWaterAnalyzer(Protocol):
    def analyze(self, route: OrderedRoute) -> list[SurfaceWaterResult]:
        ...

class GroundWaterAnalyzer(Protocol):
    def analyze(self, route: OrderedRoute) -> list[GroundWaterResult]:
        ...

class SurfaceWaterRepository(Protocol):
    def get_for_route(self, route: OrderedRoute) -> list[SurfaceWaterResult]:
        ...

class GroundWaterRepository(Protocol):
    def get_for_route(self, route: OrderedRoute) -> list[GroundWaterResult]:
        ...
