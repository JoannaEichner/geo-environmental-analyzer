from __future__ import annotations

from geo_environmental_analyzer.domain.models import OrderedRoute, GroundWaterResult
from geo_environmental_analyzer.domain.protocols import GroundWaterAnalyzer, GroundWaterRepository

class DefaultGroundWaterAnalyzer(GroundWaterAnalyzer):
    def __init__(self, repository: GroundWaterRepository) -> None:
        self._repository = repository

    def analyze(self, route: OrderedRoute) -> list[GroundWaterResult]:
        if not route.points:
            return []
        return self._repository.get_for_route(route)



