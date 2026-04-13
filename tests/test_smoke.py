from __future__ import annotations

import sys
from pathlib import Path

from geo_environmental_analyzer import main as main_module


def test_main_run_invokes_run_command(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    captured: dict[str, Path] = {}

    def fake_run_command(input_path: Path, output_path: Path, config_path: Path) -> int:
        captured["input"] = input_path
        captured["output"] = output_path
        captured["config"] = config_path
        return 0

    monkeypatch.setattr(main_module, "run_command", fake_run_command)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gea",
            "run",
            "--input",
            str(tmp_path / "input.txt"),
            "--output",
            str(tmp_path / "report.xlsx"),
            "--config",
            str(tmp_path / "settings.toml"),
        ],
    )

    result = main_module.main()

    assert result == 0
    assert captured == {
        "input": tmp_path / "input.txt",
        "output": tmp_path / "report.xlsx",
        "config": tmp_path / "settings.toml",
    }
    assert capsys.readouterr().out == ""


def test_build_parser_requires_run_subcommand() -> None:
    parser = main_module.build_parser()

    parsed = parser.parse_args(
        [
            "run",
            "--input",
            "in.txt",
            "--output",
            "out.xlsx",
            "--config",
            "settings.toml",
        ]
    )

    assert parsed.command == "run"
    assert parsed.input == Path("in.txt")
    assert parsed.output == Path("out.xlsx")
    assert parsed.config == Path("settings.toml")


def test_get_default_config_path_prefers_settings_next_to_exe(
    monkeypatch,
    tmp_path: Path,
) -> None:
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    config_path = app_dir / "settings.toml"
    config_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(
        sys, "executable", str(app_dir / "GeoEnvironmentalAnalyzer.exe")
    )

    assert main_module.get_default_config_path() == config_path


def test_get_default_config_path_uses_sibling_app_folder_for_frozen_build(
    monkeypatch,
    tmp_path: Path,
) -> None:
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    app_dir = dist_dir / "GeoEnvironmentalAnalyzer"
    app_dir.mkdir()
    config_path = app_dir / "settings.toml"
    config_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(
        sys, "executable", str(dist_dir / "GeoEnvironmentalAnalyzer.exe")
    )

    assert main_module.get_default_config_path() == config_path


def test_main_without_arguments_launches_gui(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_launch_gui(run_callback, default_config_path=Path("settings.toml")) -> int:
        captured["run_callback"] = run_callback
        captured["config"] = default_config_path
        return 0

    monkeypatch.setattr(main_module, "launch_gui", fake_launch_gui)
    monkeypatch.setattr(
        main_module, "get_default_config_path", lambda: tmp_path / "settings.toml"
    )
    monkeypatch.setattr(sys, "argv", ["gea"])

    result = main_module.main()

    assert result == 0
    assert captured["run_callback"] is main_module.run_command
    assert captured["config"] == tmp_path / "settings.toml"


def test_main_gui_subcommand_launches_gui_with_default_config(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_launch_gui(run_callback, default_config_path=Path("settings.toml")) -> int:
        captured["run_callback"] = run_callback
        captured["config"] = default_config_path
        return 0

    monkeypatch.setattr(main_module, "launch_gui", fake_launch_gui)
    monkeypatch.setattr(
        main_module, "get_default_config_path", lambda: tmp_path / "settings.toml"
    )
    monkeypatch.setattr(sys, "argv", ["gea", "gui"])

    result = main_module.main()

    assert result == 0
    assert captured["run_callback"] is main_module.run_command
    assert captured["config"] == tmp_path / "settings.toml"
