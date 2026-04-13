from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from geo_environmental_analyzer.domain.models import GroundWaterResult, OrderedRoute
from geo_environmental_analyzer.domain.protocols import GroundWaterRepository
from geo_environmental_analyzer.domain.services import (
    detect_epsg_2000,
    normalize_pl2000_coordinates,
)
from geo_environmental_analyzer.infrastructure.config import AppConfig


@dataclass(slots=True)
class JcwpdRepositoryConfig:
    spatial_path: Path
    t50_path: Path
    t4a_path: Path
    t51_path: Path
    spatial_code_field: str = "kod_jcwpd"


class FileJcwpdRepository(GroundWaterRepository):
    def __init__(
        self, app_config: AppConfig, repo_config: JcwpdRepositoryConfig
    ) -> None:
        self._app_config = app_config
        self._repo_config = repo_config

    def get_for_route(self, route: OrderedRoute) -> list[GroundWaterResult]:
        t50 = pd.DataFrame(self._read_gdbtable(self._repo_config.t50_path))
        t4a = pd.DataFrame(self._read_gdbtable(self._repo_config.t4a_path))
        t51 = pd.DataFrame(self._read_gdbtable(self._repo_config.t51_path))
        spatial_metadata = self._build_spatial_metadata()

        idx50 = self._build_index(
            t50,
            key_field="kod_jcwpd",
            fields=[
                "st_ch",
                "st_il",
                "ocena_stan",
                "id_monitor",
            ],
        )

        idx4a = self._build_index(
            t4a,
            key_field="kod_jcwpd",
            fields=["cel_st_che", "cel_st_il"],
        )

        idx51 = self._build_index(
            t51,
            key_field="kod_jcwpd",
            fields=["oc_ryz"],
        )

        found_codes: list[str] = []
        seen_codes: set[str] = set()

        for point in route.points:
            code = self._find_jcwpd_code_for_point(point.x_raw, point.y_raw)
            if not code:
                continue
            if code in seen_codes:
                continue

            seen_codes.add(code)
            found_codes.append(code)

        results: list[GroundWaterResult] = []
        for code in found_codes:
            metadata = spatial_metadata.get(code, {})
            full_code = metadata.get("full_code") or self._format_groundwater_code(code)
            number = metadata.get("number", "")
            display_name = (
                f"Jednolita część wód podziemnych nr {number} {full_code}"
                if number
                else full_code
            )

            results.append(
                GroundWaterResult(
                    code=full_code,
                    name=display_name,
                    monitored=self._monitor_flag(self._pick(idx50, code, "id_monitor")),
                    chemical_state=self._pick(idx50, code, "st_ch"),
                    quantitative_state=self._pick(idx50, code, "st_il"),
                    overall_state=self._pick(idx50, code, "ocena_stan"),
                    risk_assessment=self._pick(idx51, code, "oc_ryz"),
                    quantitative_goal=self._pick(idx4a, code, "cel_st_il"),
                    chemical_goal=self._pick(idx4a, code, "cel_st_che"),
                )
            )

        return results

    def _normalize_str(self, value: object) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        return "" if text.lower() in {"none", "nan", "<na>"} else text

    def _pick(self, index: dict[str, dict[str, str]], key: str, field: str) -> str:
        if not key:
            return ""
        record = index.get(key)
        if not record:
            return ""
        return record.get(field, "")

    def _format_groundwater_code(self, code: str) -> str:
        normalized = self._normalize_str(code)
        if not normalized:
            return ""
        if normalized.startswith("PL"):
            return normalized
        if normalized.startswith("GW"):
            return f"PL{normalized}"
        return normalized

    def _build_index(
        self,
        df: pd.DataFrame,
        key_field: str,
        fields: list[str],
    ) -> dict[str, dict[str, str]]:
        column_map = {column.lower(): column for column in df.columns}

        def resolve(name: str) -> str:
            if name in df.columns:
                return name
            alt = column_map.get(name.lower())
            if alt:
                return alt
            raise RuntimeError(f"Missing field '{name}' in columns: {list(df.columns)}")

        key_column = resolve(key_field)
        field_columns = [resolve(field) for field in fields]

        result: dict[str, dict[str, str]] = {}
        for _, row in df.iterrows():
            key = self._normalize_str(row[key_column])
            if not key or key in result:
                continue

            result[key] = {
                field_name: self._normalize_str(row[column_name])
                for field_name, column_name in zip(
                    fields, field_columns, strict=False
                )
            }

        return result

    def _read_gdbtable(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Missing geodata file: {path}")

        try:
            return gpd.read_file(str(path))
        except Exception:
            pass

        gdb_dir = path.parent
        layer_name = path.stem

        try:
            return gpd.read_file(str(gdb_dir), layer=layer_name)
        except Exception:
            pass

        try:
            layer_index = int(layer_name, 16)
            return gpd.read_file(str(gdb_dir), layer=layer_index)
        except Exception as error:
            raise RuntimeError(f"Unable to read geodata layer: {path}") from error

    def _build_spatial_metadata(self) -> dict[str, dict[str, str]]:
        gdf = self._read_gdbtable(self._repo_config.spatial_path)
        if not isinstance(gdf, gpd.GeoDataFrame):
            return {}

        column_map = {column.lower(): column for column in gdf.columns}
        code_column = column_map.get(self._repo_config.spatial_code_field.lower())
        full_code_column = column_map.get("kod_ue")
        number_column = column_map.get("nr_jcwpd")

        if code_column is None:
            return {}

        result: dict[str, dict[str, str]] = {}
        for _, row in gdf.iterrows():
            code = self._normalize_str(row[code_column])
            if not code or code in result:
                continue

            result[code] = {
                "full_code": (
                    self._normalize_str(row[full_code_column])
                    if full_code_column is not None
                    else self._format_groundwater_code(code)
                ),
                "number": (
                    self._normalize_str(row[number_column])
                    if number_column is not None
                    else ""
                ),
            }

        return result

    def _find_jcwpd_code_for_point(self, value_a: float, value_b: float) -> str:
        epsg = detect_epsg_2000(value_a, value_b)
        easting, northing = normalize_pl2000_coordinates(value_a, value_b)

        gdf = self._read_gdbtable(self._repo_config.spatial_path)
        if not isinstance(gdf, gpd.GeoDataFrame):
            return ""
        if gdf.empty or "geometry" not in gdf.columns or gdf.crs is None:
            return ""

        code_column = next(
            (
                column
                for column in gdf.columns
                if column.lower() == self._repo_config.spatial_code_field.lower()
            ),
            None,
        )
        if code_column is None:
            return ""

        point = (
            gpd.GeoSeries([Point(easting, northing)], crs=f"EPSG:{epsg}")
            .to_crs(gdf.crs)
            .iloc[0]
        )

        try:
            candidate_indexes = list(gdf.sindex.intersection(point.bounds))
            candidates = (
                gdf.iloc[candidate_indexes] if candidate_indexes else gdf.iloc[0:0]
            )
        except Exception:
            candidates = gdf

        hits = candidates[candidates.contains(point)]
        if hits.empty:
            hits = candidates[candidates.intersects(point)]

        if hits.empty:
            return ""

        return self._normalize_str(hits.iloc[0][code_column])

    def _monitor_flag(self, raw_value: str) -> str:
        value = self._normalize_str(raw_value)
        if not value:
            return "NIE"

        try:
            if float(value.replace(",", ".")) == 0.0:
                return "NIE"
        except ValueError:
            pass

        if value.lower() in {"0", "nie", "false", "brak"}:
            return "NIE"

        return "TAK"
