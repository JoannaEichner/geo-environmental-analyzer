from __future__ import annotations

from geo_environmental_analyzer.domain.models import OrderedRoute, SurfaceWaterResult
from geo_environmental_analyzer.domain.protocols import (
    SurfaceWaterAnalyzer,
    SurfaceWaterRepository,
)


class DefaultSurfaceWaterAnalyzer(SurfaceWaterAnalyzer):
    def __init__(self, repository: SurfaceWaterRepository) -> None:
        self._repository = repository

    def analyze(self, route: OrderedRoute) -> list[SurfaceWaterResult]:
        if not route.points:
            return []
        return self._repository.get_for_route(route)
