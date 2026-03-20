from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib

@dataclass(slots=True)
class PathsConfig:
    jcwp_data_dir: str
    rdos_data_dir: str
    input_dir: str
    output_dir: str

@dataclass(slots=True)
class ServicesConfig:
    uldk_url: str
    eziudp_url: str

@dataclass(slots=True)
class AnalysisConfig:
    distance_limit_km: float
    http_timeout_seconds: int

@dataclass(slots=True)
class AppConfig:
    paths: PathsConfig
    services: ServicesConfig
    analysis: AnalysisConfig
 
def _require_section(data: dict, section_name: str) -> dict:
    section = data.get(section_name)
    if not isinstance(section, dict):
        raise ValueError(f"Missing or invalid section {section_name}")
    return section

def _require_non_empty_string(section: dict, key: str) -> str:
    value = section.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing or invalid section {key}")
    return value
    
def _require_positive_number(section: dict, key: str) -> float:
    value = section.get(key)
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"Missing or invalid positive number: {key}")
    return float(value)
    
def load_settings(path: Path) -> AppConfig:

    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")
    
    with path.open("rb") as settings_file:
        data = tomllib.load(settings_file)
        paths_section = _require_section(data, "paths")
        services_section = _require_section(data, "services")
        analysis_section = _require_section(data, "analysis")
        paths = PathsConfig(
            jcwp_data_dir=_require_non_empty_string(paths_section, "jcwp_data_dir"),
        rdos_data_dir=_require_non_empty_string(paths_section, "rdos_data_dir"),
        input_dir=_require_non_empty_string(paths_section, "input_dir"),
        output_dir=_require_non_empty_string(paths_section, "output_dir"),
        )
        services = ServicesConfig(
        uldk_url=_require_non_empty_string(services_section, "uldk_url"),
        eziudp_url=_require_non_empty_string(services_section, "eziudp_url")
        )
        
        analysis = AnalysisConfig(
        distance_limit_km=_require_positive_number(analysis_section, "distance_limit_km"),
        http_timeout_seconds=int(
            _require_positive_number(analysis_section, "http_timeout_seconds"))
        )

    return AppConfig(paths=paths, services=services, analysis=analysis)






