from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point

from geo_environmental_analyzer.infrastructure.gateways.eziudp_client import (
    EziudpClient,
)
from geo_environmental_analyzer.infrastructure.gateways.uldk_client import (
    UldkClient,
)
from geo_environmental_analyzer.infrastructure.geodata.rdos_repository import (
    FileRdosRepository,
    RdosRepositoryConfig,
)


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_uldk_parse_parcel_response_returns_results() -> None:
    client = UldkClient("https://example.test", 5.0)

    results = client._parse_parcel_response(
        "0\n142807_2.0015.194\n142807_2.0015.195\n"
    )

    assert [item.parcel_id for item in results] == [
        "142807_2.0015.194",
        "142807_2.0015.195",
    ]


def test_uldk_parse_parcel_response_skips_no_result_lines() -> None:
    client = UldkClient("https://example.test", 5.0)

    results = client._parse_parcel_response("-1 brak wynikow\n")

    assert results == []


def test_uldk_get_parcel_details_uses_expected_request(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_get(url: str, params: dict[str, object], timeout: float) -> FakeResponse:
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return FakeResponse("0\nSochaczew|powiat sochaczewski|mazowieckie|Jezowka\n")

    monkeypatch.setattr(
        "geo_environmental_analyzer.infrastructure.gateways.uldk_client.requests.get",
        fake_get,
    )

    client = UldkClient("https://uldk.example.test", 25.0)
    details = client.get_parcel_details("142807_2.0015.194")

    assert captured["url"] == "https://uldk.example.test"
    assert captured["params"] == {
        "request": "GetParcelById",
        "id": "142807_2.0015.194",
        "result": "gmina,powiat,wojewodztwo,obreb",
    }
    assert captured["timeout"] == 25.0
    assert details is not None
    assert details.municipality_name == "Sochaczew"
    assert details.powiat_name == "powiat sochaczewski"
    assert details.voivodeship_name == "mazowieckie"
    assert details.cadastral_district_name == "Jezowka"


def test_eziudp_parse_wfs_url_extracts_first_url() -> None:
    client = EziudpClient("https://example.test", 5.0)

    result = client._parse_wfs_url(
        'tekst https://integracja.example.test/wfs?service=WFS&request=GetCapabilities inne'
    )

    assert result == "https://integracja.example.test/wfs?service=WFS&request=GetCapabilities"


def test_eziudp_get_wfs_url_for_powiat_uses_expected_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_get(url: str, params: dict[str, object], timeout: float) -> FakeResponse:
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return FakeResponse("https://powiat.example.test/wfs")

    monkeypatch.setattr(
        "geo_environmental_analyzer.infrastructure.gateways.eziudp_client.requests.get",
        fake_get,
    )

    client = EziudpClient("https://eziudp.example.test", 10.0)
    result = client.get_wfs_url_for_powiat("1428")

    assert captured["url"] == "https://eziudp.example.test"
    assert captured["params"] == {"teryt": "1428", "rodzaj": "powiaty"}
    assert captured["timeout"] == 10.0
    assert result == "https://powiat.example.test/wfs"


def test_rdos_load_layers_reads_shapefiles_and_reprojects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_dir = tmp_path / "rdos"
    layer_dir = data_dir / "Rezerwaty"
    layer_dir.mkdir(parents=True)
    shp_path = layer_dir / "RezerwatyPolygon.shp"
    shp_path.write_text("placeholder", encoding="utf-8")

    source_gdf = gpd.GeoDataFrame(
        {"nazwa": ["Testowy rezerwat"]},
        geometry=[Point(1, 1)],
        crs="EPSG:4326",
    )

    def fake_read_shapefile(self: FileRdosRepository, path: Path) -> gpd.GeoDataFrame | None:
        assert path == shp_path
        return source_gdf

    monkeypatch.setattr(FileRdosRepository, "_read_shapefile", fake_read_shapefile)

    repository = FileRdosRepository(RdosRepositoryConfig(data_dir=data_dir, work_epsg=2180))
    layers = repository.load_layers()

    assert len(layers) == 1
    assert layers[0].source_name == str(Path("Rezerwaty") / "RezerwatyPolygon.shp")
    assert layers[0].gdf.crs.to_epsg() == 2180


def test_rdos_load_layers_raises_for_missing_directory(tmp_path: Path) -> None:
    repository = FileRdosRepository(RdosRepositoryConfig(data_dir=tmp_path / "missing"))

    with pytest.raises(FileNotFoundError, match="RDOS data directory not found"):
        repository.load_layers()


def test_rdos_load_layers_raises_for_directory_without_shapefiles(tmp_path: Path) -> None:
    data_dir = tmp_path / "rdos_empty"
    data_dir.mkdir()

    repository = FileRdosRepository(RdosRepositoryConfig(data_dir=data_dir))

    with pytest.raises(RuntimeError, match="No RDOS shapefiles found"):
        repository.load_layers()
