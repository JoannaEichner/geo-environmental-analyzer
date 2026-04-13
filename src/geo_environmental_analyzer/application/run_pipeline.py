from __future__ import annotations

from pathlib import Path

from geo_environmental_analyzer.domain.models import AnalysisBundle
from geo_environmental_analyzer.domain.protocols import (
    GroundWaterAnalyzer,
    ParcelAnalyzer,
    PointReader,
    ProtectedAreaAnalyzer,
    SurfaceWaterAnalyzer,
)
from geo_environmental_analyzer.domain.services import build_ordered_route


class RunAnalysisPipeline:
    def __init__(
        self,
        point_reader: PointReader,
        parcel_analyzer: ParcelAnalyzer,
        surface_water_analyzer: SurfaceWaterAnalyzer,
        ground_water_analyzer: GroundWaterAnalyzer,
        protected_area_analyzer: ProtectedAreaAnalyzer,
    ) -> None:
        self._point_reader = point_reader
        self._parcel_analyzer = parcel_analyzer
        self._surface_water_analyzer = surface_water_analyzer
        self._ground_water_analyzer = ground_water_analyzer
        self._protected_area_analyzer = protected_area_analyzer

    def run(self, input_path: Path) -> AnalysisBundle:
        points = self._point_reader.read(input_path)

        route = build_ordered_route(points)

        parcels = self._parcel_analyzer.analyze(route)
        surface_water = self._surface_water_analyzer.analyze(route)
        groundwater = self._ground_water_analyzer.analyze(route)
        protected_areas = self._protected_area_analyzer.analyze(route)

        return AnalysisBundle(
            route=route,
            parcels=parcels,
            surface_water=surface_water,
            groundwater=groundwater,
            protected_areas=protected_areas,
        )
