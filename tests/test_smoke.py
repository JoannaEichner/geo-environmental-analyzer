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
        ["run", "--input", "in.txt", "--output", "out.xlsx", "--config", "settings.toml"]
    )

    assert parsed.command == "run"
    assert parsed.input == Path("in.txt")
    assert parsed.output == Path("out.xlsx")
    assert parsed.config == Path("settings.toml")
