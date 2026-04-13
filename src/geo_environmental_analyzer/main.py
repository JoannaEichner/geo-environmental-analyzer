from __future__ import annotations

import argparse
import sys
from pathlib import Path

from geo_environmental_analyzer.analyses.groundwater import DefaultGroundWaterAnalyzer
from geo_environmental_analyzer.analyses.parcels import DefaultParcelAnalyzer
from geo_environmental_analyzer.analyses.protected_areas import (
    DefaultProtectedAreaAnalyzer,
)
from geo_environmental_analyzer.analyses.surface_water import (
    DefaultSurfaceWaterAnalyzer,
)
from geo_environmental_analyzer.application.run_pipeline import RunAnalysisPipeline
from geo_environmental_analyzer.gui import launch_gui
from geo_environmental_analyzer.infrastructure.config import AppConfig, load_settings
from geo_environmental_analyzer.infrastructure.gateways.uldk_client import UldkClient
from geo_environmental_analyzer.infrastructure.geodata.jcwp_repository import (
    FileJcwpRepository,
    JcwpRepositoryConfig,
)
from geo_environmental_analyzer.infrastructure.geodata.jcwpd_repository import (
    FileJcwpdRepository,
    JcwpdRepositoryConfig,
)
from geo_environmental_analyzer.infrastructure.geodata.rdos_repository import (
    FileRdosRepository,
    RdosRepositoryConfig,
)
from geo_environmental_analyzer.infrastructure.input.points_txt import TxtPointReader
from geo_environmental_analyzer.infrastructure.reporting.xlsx_writer import (
    XlsxReportWriter,
)


def get_application_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def get_default_config_path() -> Path:
    app_root = get_application_root()
    executable_name = Path(sys.executable).stem if getattr(sys, "frozen", False) else ""

    candidates = [app_root / "settings.toml"]
    if executable_name:
        candidates.append(app_root / executable_name / "settings.toml")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


def resolve_configured_path(config_path: Path, configured_value: str) -> Path:
    path = Path(configured_value)
    if path.is_absolute():
        return path
    return config_path.parent / path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gea")
    subparsers = parser.add_subparsers(dest="command", required=False)

    run_parser = subparsers.add_parser(
        "run",
        help="Run full environmental analysis.",
    )
    run_parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Input TXT file.",
    )
    run_parser.add_argument(
        "--output", required=True, type=Path, help="Output XLSX file."
    )
    run_parser.add_argument(
        "--config",
        default=get_default_config_path(),
        type=Path,
        help="Path to settings TOML file.",
    )

    subparsers.add_parser(
        "gui",
        help="Open the desktop application window.",
    )

    return parser


def build_pipeline(config: AppConfig, config_path: Path) -> RunAnalysisPipeline:
    waters_dir = resolve_configured_path(config_path, config.paths.waters_data_dir)
    rdos_dir = resolve_configured_path(config_path, config.paths.rdos_data_dir)

    parcel_analyzer = DefaultParcelAnalyzer(
        UldkClient(config.services.uldk_url, config.analysis.http_timeout_seconds)
    )

    surface_water_analyzer = DefaultSurfaceWaterAnalyzer(
        FileJcwpRepository(
            config,
            JcwpRepositoryConfig(
                spatial_candidates=sorted(waters_dir.glob("*.gdbtable")),
                t41_path=waters_dir / "a00000041.gdbtable",
                t4c_path=waters_dir / "a0000004c.gdbtable",
                t4b_path=waters_dir / "a0000004b.gdbtable",
            ),
        )
    )

    ground_water_analyzer = DefaultGroundWaterAnalyzer(
        FileJcwpdRepository(
            config,
            JcwpdRepositoryConfig(
                spatial_path=waters_dir / "a0000001a.gdbtable",
                t50_path=waters_dir / "a00000050.gdbtable",
                t4a_path=waters_dir / "a0000004a.gdbtable",
                t51_path=waters_dir / "a00000051.gdbtable",
            ),
        )
    )

    protected_area_analyzer = DefaultProtectedAreaAnalyzer(
        FileRdosRepository(RdosRepositoryConfig(data_dir=rdos_dir)),
        distance_limit_km=config.analysis.distance_limit_km,
    )

    return RunAnalysisPipeline(
        point_reader=TxtPointReader(),
        parcel_analyzer=parcel_analyzer,
        surface_water_analyzer=surface_water_analyzer,
        ground_water_analyzer=ground_water_analyzer,
        protected_area_analyzer=protected_area_analyzer,
    )


def run_command(input_path: Path, output_path: Path, config_path: Path) -> int:
    resolved_config_path = config_path.resolve()
    config = load_settings(resolved_config_path)
    pipeline = build_pipeline(config, resolved_config_path)
    writer = XlsxReportWriter()

    bundle = pipeline.run(input_path)
    writer.write(bundle, output_path)

    print(f"Report written to: {output_path}")
    return 0


def main() -> int:
    if len(sys.argv) == 1:
        return launch_gui(run_command, get_default_config_path())

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        return run_command(args.input, args.output, args.config)

    if args.command == "gui":
        return launch_gui(run_command, get_default_config_path())

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
