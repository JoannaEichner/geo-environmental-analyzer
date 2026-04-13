from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from geo_environmental_analyzer.domain.models import OrderedRoute, SurfaceWaterResult
from geo_environmental_analyzer.domain.protocols import SurfaceWaterRepository
from geo_environmental_analyzer.domain.services import (
    detect_epsg_2000,
    normalize_pl2000_coordinates,
)
from geo_environmental_analyzer.infrastructure.config import AppConfig


@dataclass(slots=True)
class JcwpRepositoryConfig:
    spatial_candidates: list[Path]
    t41_path: Path
    t4c_path: Path
    t4b_path: Path
    spatial_ms_kod_field: str = "MS_KOD"


class FileJcwpRepository(SurfaceWaterRepository):
    def __init__(
        self, app_config: AppConfig, repo_config: JcwpRepositoryConfig
    ) -> None:
        self._app_config = app_config
        self._repo_config = repo_config

    def get_for_route(self, route: OrderedRoute) -> list[SurfaceWaterResult]:
        t41 = pd.DataFrame(self._read_gdbtable(self._repo_config.t41_path))
        t4c = pd.DataFrame(self._read_gdbtable(self._repo_config.t4c_path))
        t4b = pd.DataFrame(self._read_gdbtable(self._repo_config.t4b_path))
        idx41 = self._build_index(
            t41,
            key_field="ms_kod",
            fields=[
                "nazwa_jcwp",
                "ms_kod",
                "dorz",
                "regwod",
                "rzgw",
                "zz",
                "nw",
                "monit_jcwp",
                "status_n",
                "st_eko",
                "st_chem",
            ],
        )

        idx4c = self._build_index(
            t4c,
            key_field="kod_jcwp",
            fields=[
                "nazwa_jcwp",
                "jcwp_zmian",
                "typ_jcwp",
                "reg_wodny",
                "rzgw",
                "rdos",
                "st_eko",
                "st_chem",
                "ocena_stan",
                "oc_ryz",
            ],
        )

        idx4b = self._build_index(
            t4b,
            key_field="kod_jcwp",
            fields=["cel_st_eko", "cel_st_che"],
        )
        found_codes: list[str] = []
        seen_codes: set[str] = set()

        for point in route.points:
            ms_kod = self._find_ms_kod_for_point(point.x_raw, point.y_raw)
            if not ms_kod:
                continue
            if ms_kod in seen_codes:
                continue
            seen_codes.add(ms_kod)
            found_codes.append(ms_kod)

        results: list[SurfaceWaterResult] = []
        for ms_kod in found_codes:
            name = self._pick(idx41, ms_kod, "nazwa_jcwp") or self._pick(
                idx4c, ms_kod, "nazwa_jcwp"
            )

            results.append(
                SurfaceWaterResult(
                    code=self._format_surface_code(ms_kod),
                    name=name,
                    status=self._pick(idx41, ms_kod, "status_n"),
                    monitored=self._pick(idx41, ms_kod, "monit_jcwp"),
                    overall_state=self._pick(idx4c, ms_kod, "ocena_stan"),
                    risk_assessment=self._pick(idx4c, ms_kod, "oc_ryz"),
                    ecological_potential_goal=self._pick(idx4b, ms_kod, "cel_st_eko"),
                    chemical_goal=self._pick(idx4b, ms_kod, "cel_st_che"),
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

    def _format_surface_code(self, code: str) -> str:
        normalized = self._normalize_str(code)
        if not normalized:
            return ""
        if normalized.startswith("PL"):
            return normalized
        if normalized.startswith("RW"):
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

    def _find_ms_kod_for_point(self, value_a: float, value_b: float) -> str:
        epsg = detect_epsg_2000(value_a, value_b)
        easting, northing = normalize_pl2000_coordinates(value_a, value_b)

        for spatial_path in self._repo_config.spatial_candidates:
            if not spatial_path.exists():
                continue

            gdf = self._read_gdbtable(spatial_path)
            if not isinstance(gdf, gpd.GeoDataFrame):
                continue
            if gdf.empty or "geometry" not in gdf.columns or gdf.crs is None:
                continue

            code_column = next(
                (
                    column
                    for column in gdf.columns
                    if column.upper() == self._repo_config.spatial_ms_kod_field.upper()
                ),
                None,
            )
            if code_column is None:
                continue

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
                continue

            return self._normalize_str(hits.iloc[0][code_column])

        return ""
