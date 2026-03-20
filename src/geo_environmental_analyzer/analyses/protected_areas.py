from __future__ import annotations

from pyproj import Transformer
from shapely.geometry import Point

from geo_environmental_analyzer.domain.models import OrderedRoute, ProtectedAreaDistance
from geo_environmental_analyzer.domain.protocols import ProtectedAreaAnalyzer
from geo_environmental_analyzer.domain.services import (
    detect_epsg_2000,
    normalize_pl2000_coordinates,
)
from geo_environmental_analyzer.infrastructure.geodata.rdos_repository import (
    FileRdosRepository,
    RdosLayer,
)

CATEGORY_LABELS = {
    "ObszaryChronionegoKrajobrazu": "Obszar chronionego krajobrazu",
    "ObszarySpecjalnejOchrony": "Natura 2000 OSO",
    "SpecjalneObszaryOchrony": "Natura 2000 SOO",
    "ParkiKrajobrazowe": "Park krajobrazowy",
    "ParkiNarodowe": "Park narodowy",
    "Rezerwaty": "Rezerwat przyrody",
    "StanowiskaDokumentacyjne": "Stanowisko dokumentacyjne",
    "UzytkiEkologiczne": "Uzytek ekologiczny",
    "ZespolyPrzyrodniczoKrajobrazowe": "Zespol przyrodniczo-krajobrazowy",
}

NAME_FIELDS = ("nazwa", "NAZWA", "name", "NAME")


class DefaultProtectedAreaAnalyzer(ProtectedAreaAnalyzer):
    def __init__(
        self,
        repository: FileRdosRepository,
        distance_limit_km: float,
        work_epsg: int = 2180,
    ) -> None:
        self._repository = repository
        self._distance_limit_km = distance_limit_km
        self._work_epsg = work_epsg

    def analyze(self, route: OrderedRoute) -> list[ProtectedAreaDistance]:
        if not route.points:
            return []

        layers = self._repository.load_layers()
        limit_m = self._distance_limit_km * 1000
        min_distances: dict[str, float] = {}

        for route_point in route.points:
            point = self._to_work_point(route_point.x_raw, route_point.y_raw)
            for layer in layers:
                for feature_name, distance in self._feature_distances(
                    point, layer, limit_m
                ).items():
                    current = min_distances.get(feature_name)
                    if current is None or distance < current:
                        min_distances[feature_name] = distance

        return [
            ProtectedAreaDistance(
                form_name=feature_name,
                distance_km=round(distance_m / 1000, 2),
            )
            for feature_name, distance_m in sorted(
                min_distances.items(),
                key=lambda item: (item[1], item[0]),
            )
        ]

    def _category_label(self, source_name: str) -> str:
        normalized = source_name.replace("\\", "/")
        root = normalized.split("/", 1)[0]
        return CATEGORY_LABELS.get(root, root)

    def _to_work_point(self, value_a: float, value_b: float) -> Point:
        epsg = detect_epsg_2000(value_a, value_b)
        easting, northing = normalize_pl2000_coordinates(value_a, value_b)

        if epsg == self._work_epsg:
            return Point(easting, northing)

        transformer = Transformer.from_crs(
            f"EPSG:{epsg}",
            f"EPSG:{self._work_epsg}",
            always_xy=True,
        )
        x, y = transformer.transform(easting, northing)
        return Point(x, y)

    def _feature_distances(
        self,
        point: Point,
        layer: RdosLayer,
        limit_m: float,
    ) -> dict[str, float]:
        gdf = layer.gdf
        search_area = point.buffer(limit_m)

        try:
            candidate_indexes = list(gdf.sindex.intersection(search_area.bounds))
            candidates = (
                gdf.iloc[candidate_indexes] if candidate_indexes else gdf.iloc[0:0]
            )
        except Exception:
            candidates = gdf

        if candidates.empty:
            return {}

        distances: dict[str, float] = {}
        for _, feature in candidates.iterrows():
            geometry = feature.geometry
            if geometry is None:
                continue

            distance = float(geometry.distance(point))
            if distance > limit_m:
                continue

            feature_name = self._feature_name(layer, feature)
            current = distances.get(feature_name)
            if current is None or distance < current:
                distances[feature_name] = distance

        return distances

    def _feature_name(self, layer: RdosLayer, feature: object) -> str:
        raw_name = ""
        for field_name in NAME_FIELDS:
            if field_name in layer.gdf.columns:
                value = str(feature[field_name]).strip()
                if value and value.lower() not in {"none", "nan", "<na>"}:
                    raw_name = value
                    break

        category = self._category_label(layer.source_name)
        return self._compose_display_name(category, raw_name)

    def _compose_display_name(self, category: str, raw_name: str) -> str:
        name = raw_name.strip()
        if not name:
            return category

        category_lower = category.lower()
        name_lower = name.lower()

        if category_lower in name_lower or name_lower in category_lower:
            return name

        if category.startswith("Natura 2000"):
            return f'{category} "{name}"'

        if category == "Rezerwat przyrody":
            return f'{category} "{name}"'

        return f"{category} {name}"
