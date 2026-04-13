from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from geo_environmental_analyzer.infrastructure.config import load_settings


def launch_gui(run_callback, default_config_path: Path = Path("settings.toml")) -> int:
    app = ReportGeneratorApp(run_callback, default_config_path)
    app.run()
    return 0


class ReportGeneratorApp:
    def __init__(self, run_callback, default_config_path: Path) -> None:
        self._run_callback = run_callback
        self._config_path = default_config_path
        self._root = tk.Tk()
        self._root.title("Geo Environmental Analyzer")
        self._root.geometry("760x420")
        self._root.resizable(False, False)

        self._input_var = tk.StringVar()
        self._output_var = tk.StringVar()
        self._status_var = tk.StringVar(
            value="Wybierz plik TXT ze wspolrzednymi, a potem kliknij Generuj raport."
        )

        self._generate_button: ttk.Button | None = None

        self._configure_style()
        self._build_layout()
        self._sync_output_with_settings()

    def run(self) -> None:
        self._root.mainloop()

    def _configure_style(self) -> None:
        self._root.configure(background="#f6f7fb")

        style = ttk.Style(self._root)
        available_themes = set(style.theme_names())
        if "clam" in available_themes:
            style.theme_use("clam")

        style.configure("App.TFrame", background="#f6f7fb")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure(
            "Title.TLabel", background="#f6f7fb", font=("Segoe UI", 18, "bold")
        )
        style.configure("Body.TLabel", background="#f6f7fb", font=("Segoe UI", 10))
        style.configure(
            "Section.TLabel", background="#ffffff", font=("Segoe UI", 10, "bold")
        )
        style.configure("StatusCard.TFrame", background="#eef4ff")
        style.configure(
            "Status.TLabel",
            background="#eef4ff",
            font=("Segoe UI", 10),
        )
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        frame = ttk.Frame(self._root, padding=20, style="App.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)

        ttk.Label(
            frame,
            text="Geo Environmental Analyzer",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            frame,
            text=(
                "Wybierz plik TXT z trasa. Program sam wczyta settings.toml, "
                "wykorzysta dane srodowiskowe i przygotuje raport XLSX."
            ),
            style="Body.TLabel",
            wraplength=700,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(6, 16))

        card = ttk.Frame(frame, padding=18, style="Card.TFrame")
        card.grid(row=2, column=0, sticky="ew")
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Plik TXT", style="Section.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        ttk.Entry(card, textvariable=self._input_var, width=72).grid(
            row=1,
            column=0,
            sticky="we",
            padx=(0, 10),
        )
        ttk.Button(card, text="Wybierz plik", command=self._choose_input).grid(
            row=1,
            column=1,
            sticky="we",
        )

        ttk.Label(card, text="Plik wynikowy XLSX", style="Section.TLabel").grid(
            row=2,
            column=0,
            sticky="w",
            pady=(14, 6),
        )
        ttk.Entry(card, textvariable=self._output_var, width=72).grid(
            row=3,
            column=0,
            sticky="we",
            padx=(0, 10),
        )
        ttk.Button(card, text="Zmien lokalizacje", command=self._choose_output).grid(
            row=3,
            column=1,
            sticky="we",
        )

        ttk.Label(
            card,
            text=f"Konfiguracja laduje sie automatycznie z: {self._config_path}",
            style="Body.TLabel",
            wraplength=680,
            justify="left",
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(14, 0))

        self._generate_button = ttk.Button(
            frame,
            text="Generuj raport",
            command=self._start_generation,
            style="Primary.TButton",
        )
        self._generate_button.grid(row=3, column=0, sticky="ew", pady=(16, 12))

        status_frame = ttk.Frame(frame, padding=14, style="StatusCard.TFrame")
        status_frame.grid(row=4, column=0, sticky="ew")

        ttk.Label(
            status_frame,
            textvariable=self._status_var,
            style="Status.TLabel",
            wraplength=680,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

    def _choose_input(self) -> None:
        selected = filedialog.askopenfilename(
            title="Wybierz plik TXT",
            filetypes=[("Pliki TXT", "*.txt"), ("Wszystkie pliki", "*.*")],
        )
        if not selected:
            return

        self._input_var.set(selected)
        self._sync_output_with_settings()

    def _choose_output(self) -> None:
        suggested = self._suggest_output_path()
        selected = filedialog.asksaveasfilename(
            title="Zapisz raport XLSX",
            defaultextension=".xlsx",
            initialfile=suggested.name,
            initialdir=str(suggested.parent),
            filetypes=[("Pliki XLSX", "*.xlsx")],
        )
        if selected:
            self._output_var.set(selected)

    def _suggest_output_path(self) -> Path:
        input_text = self._input_var.get().strip()

        input_path = Path(input_text) if input_text else Path("report.txt")
        input_stem = input_path.stem or "report"

        output_dir = Path.cwd()
        try:
            settings = load_settings(self._config_path)
            configured_output_dir = Path(settings.paths.output_dir)
            if not configured_output_dir.is_absolute():
                configured_output_dir = self._config_path.parent / configured_output_dir
            output_dir = configured_output_dir
        except Exception:
            output_dir = Path.cwd()

        return output_dir / f"{input_stem}_report.xlsx"

    def _sync_output_with_settings(self) -> None:
        self._output_var.set(str(self._suggest_output_path()))

    def _start_generation(self) -> None:
        input_path = Path(self._input_var.get().strip())
        output_path = Path(self._output_var.get().strip())

        if not input_path.name:
            messagebox.showerror("Brak pliku", "Wybierz plik TXT z punktami.")
            return
        if not output_path.name:
            messagebox.showerror("Brak pliku", "Wskaz plik wynikowy XLSX.")
            return
        if not self._config_path.exists():
            messagebox.showerror(
                "Brak konfiguracji",
                f"Nie znaleziono pliku settings.toml:\n{self._config_path}",
            )
            return

        if self._generate_button is not None:
            self._generate_button.state(["disabled"])
        self._status_var.set("Trwa generowanie raportu. To moze potrwac chwile...")

        worker = threading.Thread(
            target=self._run_generation,
            args=(input_path, output_path, self._config_path),
            daemon=True,
        )
        worker.start()

    def _run_generation(
        self,
        input_path: Path,
        output_path: Path,
        config_path: Path,
    ) -> None:
        try:
            self._run_callback(input_path, output_path, config_path)
        except Exception as error:
            self._root.after(0, self._handle_error, error)
            return

        self._root.after(0, self._handle_success, output_path)

    def _handle_success(self, output_path: Path) -> None:
        if self._generate_button is not None:
            self._generate_button.state(["!disabled"])
        self._status_var.set(f"Raport zapisany: {output_path}")
        messagebox.showinfo("Gotowe", f"Raport zostal zapisany w:\n{output_path}")

    def _handle_error(self, error: Exception) -> None:
        if self._generate_button is not None:
            self._generate_button.state(["!disabled"])
        self._status_var.set("Wystapil blad podczas generowania raportu.")
        messagebox.showerror("Blad", str(error))
