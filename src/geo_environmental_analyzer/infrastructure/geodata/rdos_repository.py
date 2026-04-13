from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd


@dataclass(slots=True)
class RdosRepositoryConfig:
    data_dir: Path
    work_epsg: int = 2180


@dataclass(slots=True)
class RdosLayer:
    source_name: str
    gdf: gpd.GeoDataFrame


class FileRdosRepository:
    def __init__(self, repo_config: RdosRepositoryConfig) -> None:
        self._repo_config = repo_config

    def load_layers(self) -> list[RdosLayer]:
        if not self._repo_config.data_dir.exists():
            raise FileNotFoundError(
                f"RDOS data directory not found: {self._repo_config.data_dir}"
            )

        shp_files = sorted(self._repo_config.data_dir.rglob("*.shp"))
        if not shp_files:
            raise RuntimeError(
                f"No RDOS shapefiles found in: {self._repo_config.data_dir}"
            )

        layers: list[RdosLayer] = []

        for shp_path in shp_files:
            gdf = self._read_shapefile(shp_path)
            if gdf is None or gdf.empty or "geometry" not in gdf.columns:
                continue

            if gdf.crs is not None:
                gdf = gdf.to_crs(epsg=self._repo_config.work_epsg)

            layers.append(
                RdosLayer(
                    source_name=str(shp_path.relative_to(self._repo_config.data_dir)),
                    gdf=gdf,
                )
            )

        if not layers:
            raise RuntimeError("No valid RDOS layers were loaded.")

        return layers

    def _read_shapefile(self, shp_path: Path) -> gpd.GeoDataFrame | None:
        for encoding in ("cp1250", "utf-8", None):
            try:
                kwargs = {"encoding": encoding} if encoding else {}
                return gpd.read_file(shp_path, **kwargs)
            except Exception:
                continue
        return None
