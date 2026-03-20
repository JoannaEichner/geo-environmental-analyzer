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

class SurfaceWaterAnalyzer(Protocol):
    def analyze(self, route: OrderedRoute) -> SurfaceWaterResult | None:
        ...

class GroundWaterAnalyzer(Protocol):
    def analyze(self, route: OrderedRoute) -> GroundWaterResult | None:
        ...

class ProtectedAreaAnalyzer(Protocol):
    def analyze(self, route: OrderedRoute) -> list[ProtectedAreaDistance]:
        ...

class ReportWriter(Protocol):
    def write(self, bundle: AnalysisBundle, output_path: Path) -> None:
        ...

class SurfaceWaterRepository(Protocol):
    def get_for_route(self, route: OrderedRoute) -> SurfaceWaterResult | None:
        ...

class GroundWaterRepository(Protocol):
    def get_for_route(self, route: OrderedRoute) -> GroundWaterResult | None:
        ...

class ProtectedAreaRepository(Protocol):
    def get_for_route(self, route: OrderedRoute) -> list[ProtectedAreaDistance]:
        ...

class ParcelRepository(Protocol):
    def get_for_route(self, route: OrderedRoute) -> list[ParcelRecord]:
        ...
